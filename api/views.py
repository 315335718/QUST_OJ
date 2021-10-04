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
from django.contrib.auth import authenticate
from django.views import View
# from django.http import HttpResponse

from account.models import User
from problem.models import Problem
from contest.models import ContestManager, Contest, ContestParticipant, ContestProblem
from submission.models import Submission
from schoolclass.models import SchoolClass
from comment.models import Article, Comment
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


# class SubmissionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Submission
#         fields = ("code", "problem", "create_time", "code_length", "status", "status_percent", "status_message", "ip")
#
#
# class SubmissionsView(APIView):
#     permission_classes = (IsAuthenticated,)
#
#     def post(self, request):
#         submissions = Submission.objects.all()
#         serializer = SubmissionSerializer(submissions, many=True)
#         return Response(serializer.data)


class TestView2(APIView):
    def get(self, request, *args, **kwargs):
        print(request.data)
        return Response({"status": True})


def get_or_create_username_and_id(openid, avatar_url):
    if User.objects.filter(wx_openid=openid).exists():
        user = User.objects.get(wx_openid=openid)
        return user.username, user.id, user.wx_password
    else:
        ticks = int(time.time())
        random_str = str(ticks) + chr(ord('a') + random.randint(0, 25)) + chr(ord('a') + random.randint(0, 25))
        username = 'wexin_' + random_str
        password = make_password(openid)
        fake_email = random_str + '@' + 'qq.com'
        user = User.objects.create(username=username, password=password, email=fake_email, wx_openid=openid, \
                                   wx_avatar_url=avatar_url, wx_password=openid, wx_stuff=1)
        return user.username, user.id, user.wx_password


class WxLoginView(APIView):
    def post(self, request):
        jscode = request.POST.get('code')
        avatar_url = request.POST.get('avatar_url')
        url = 'https://api.weixin.qq.com/sns/jscode2session'
        url = url + "?appid=" + WX_APP_ID + "&secret=" + WX_APP_SECRET + "&js_code=" + jscode + "&grant_type=authorization_code"
        res = requests.get(url).json()
        if 'errcode' in res.keys():
            return Response({'flag': 0})
        openid = res['openid']
        username, user_id, wx_password = get_or_create_username_and_id(openid, avatar_url)
        data = {
            'username': username,
            'password': wx_password,
        }
        res = requests.post('https://www.qustoj.cn/api/token/', data=data)
        # res = requests.post('http://127.0.0.1:8000/api/token/', data=data)
        token = res.json()
        contents = {
            'flag': 1,
            'token': token,
            'user_id': user_id,
        }
        return Response(contents)


class WxBindingView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        user_id = request.POST.get('user_id', 0)
        if int(user_id) == 0:
            return Response({'flag': 0, 'message': '检查是否登录或网络连接是否正常'})  # 检查是否未登录
        now_user = User.objects.get(id=user_id)
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if len(username) < 1 or len(password) < 1:
            return Response({'flag': 0, 'message': '缺少用户名或密码'})
        try:
            has_user = User.objects.get(username=username)
        except:
            return Response({'flag': 0, 'message': '该用户不存在'})
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'flag': 0, 'message': '用户名或密码错误'})
        try:
            has_user.wx_openid = now_user.wx_openid
            has_user.wx_avatar_url = now_user.wx_avatar_url
            has_user.wx_password = password
            ContestParticipant.objects.filter(user_id=now_user.id).update(user_id=has_user.id)
            SchoolClass.objects.filter(tercher_id=now_user.id).update(tercher_id=has_user.id)
            Submission.objects.filter(author_id=now_user.id).update(author_id=has_user.id)
            Article.objects.filter(author_id=now_user.id).update(author_id=has_user.id)
            Comment.objects.filter(author_id=now_user.id).update(author_id=has_user.id)
            data = {
                'username': has_user.username,
                'password': now_user.wx_openid,
            }
            now_user.wx_openid = ''
            now_user.wx_avatar_url = ''
            now_user.save(update_fields=['wx_openid', 'wx_avatar_url'])
            has_user.save(update_fields=['wx_openid', 'wx_avatar_url', 'wx_password'])
            res = requests.post('https://www.qustoj.cn/api/token/', data=data)
            token = res.json()
        except Exception as e:
            return Response({'flag': 0, 'message': '系统错误: ' + str(str(e).encode())})
        return Response({'flag': 1, 'message': '操作成功', 'token': token, 'user_id': has_user.id})