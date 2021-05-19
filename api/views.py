from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.views import View
# from django.http import HttpResponse

from problem.models import Problem
from submission.models import Submission


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


class ProblemListView(APIView):
    # permission_classes = (IsAuthenticated,)
    def get(self, request):
        print(request.GET.get('mname', 'world'))
        problem_list = Problem.objects.all().only('id', 'title', 'description', 'problem_type', 'level', 'ac_count', \
                                                  'total_count').order_by('id')
        # if not is_admin_or_root(self.request.user):
        #     queryset = queryset.filter(visible=True)
        serializer = ProblemSerializer(problem_list, many=True)
        return Response({'problem_list': serializer.data})


class ProblemView(APIView):
    # permission_classes = (IsAuthenticated,)
    def get(self, request):
        id = request.GET.get('pid', 1)
        problem = Problem.objects.get(pk=id)
        serializer = ProblemSerializer(problem)
        return Response({'problem': serializer.data})