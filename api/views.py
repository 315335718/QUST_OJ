import requests
import time
import random

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.views import View
# from django.http import HttpResponse

from account.models import User
from problem.models import Problem
from submission.models import Submission
from QUST_OJ.settings import WX_APP_ID, WX_APP_SECRET


# class HelloView(View):
#     def get(self, request, *args, **kwargs):
#         return HttpResponse('hello')

class TestView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        print('authenticators:', request.authenticators)
        print('successful_authenticator:', request.successful_authenticator)
        print('authenticate: ', request.successful_authenticator.authenticate(request))
        print('authenticate_header: ', request.successful_authenticator.authenticate_header(request))
        print('get_header: ', request.successful_authenticator.get_header(request))
        print('get_raw_token: ',
              request.successful_authenticator.get_raw_token(request.successful_authenticator.get_header(request)))
        print('get_validated_token: ', request.successful_authenticator.get_validated_token(
            request.successful_authenticator.get_raw_token(request.successful_authenticator.get_header(request))))
        print('get_user: ', request.successful_authenticator.get_user(
            request.successful_authenticator.get_validated_token(
                request.successful_authenticator.get_raw_token(request.successful_authenticator.get_header(request)))))
        print('www_authenticate_realm: ', request.successful_authenticator.www_authenticate_realm)
        return Response("OK")


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ("id", "title", "description", "problem_type", "level", "ac_count", "total_count")


# class ProblemListView(APIView):
#     # permission_classes = (IsAuthenticated,)
#     def get(self, request):
#         problem_list = Problem.objects.all().only('id', 'title', 'description', 'problem_type', 'level', 'ac_count', \
#                                                   'total_count').order_by('id')
#         # if not is_admin_or_root(self.request.user):
#         #     queryset = queryset.filter(visible=True)
#         serializer = ProblemSerializer(problem_list, many=True)
#         return Response(serializer.data)


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ("code", "problem", "create_time", "code_length", "status", "status_percent", "status_message", "ip")


class SubmissionsView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        submissions = Submission.objects.all()
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


class TestView2(APIView):
    def get(self, request, *args, **kwargs):
        print(request.data)
        return Response({"status": True})


def get_or_create_username_and_id(openid):
    if User.objects.filter(wx_openid=openid).exists():
        user = User.objects.get(wx_openid=openid)
        return user.username, user.id
    else:
        ticks = int(time.time())
        random_str = str(ticks) + str(random.randint(1, 100)) + chr(ord('a') + random.randint(0, 25))
        username = 'wexin_' + random_str
        password = make_password(openid)
        fake_email = random_str + '@' + 'qq.com'
        print(username)
        user = User.objects.create(username=username, password=password, email=fake_email, wx_openid=openid)
        return user.username, user.id


class WxLoginView(APIView):
    def post(self, request):
        jscode = request.POST.get('code')
        url = 'https://api.weixin.qq.com/sns/jscode2session'
        url = url + "?appid=" + WX_APP_ID + "&secret=" + WX_APP_SECRET + "&js_code=" + jscode + "&grant_type=authorization_code"
        res = requests.get(url).json()
        if 'errcode' in res.keys():
            return Response({'flag': 0})
        openid = res['openid']
        username, user_id = get_or_create_username_and_id(openid)
        data = {
            'username': username,
            'password': openid,
        }
        res = requests.post('https://www.qustoj.cn/api/token/', data=data)
        token = res.json()
        contents = {
            'flag': 1,
            'token': token,
            'user_id': user_id,
        }
        print(contents)
        return Response(contents)
