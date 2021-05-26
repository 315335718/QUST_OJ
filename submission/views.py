from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Q
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from submission.models import Submission
from account.models import User


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class SubmissionSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    class Meta:
        model = Submission
        fields = ('id', 'create_time', 'judge_end_time', 'author_id', 'problem_id', 'status', 'status_percent', \
                  'status_message', 'author')


class GetAllSubmissionView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Submission.objects.all()[:50].select_related('problem', 'author'). \
            only('id', 'create_time', 'judge_end_time', 'author__id', 'author__username', 'problem__id', 'status', \
                 'status_percent', 'status_message')
        serializer = SubmissionSerializer(queryset, many=True)
        return Response(serializer.data)


class GetOneProblemSubmissionView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['u_id']
        problem_id = self.kwargs['p_id']
        queryset = Submission.objects.filter(Q(author_id=user_id) & Q(problem_id=problem_id) & Q(contest_id=None))[:5].\
            select_related('author').only('id', 'create_time', 'judge_end_time', 'problem_id', 'status', 'status_percent', 'status_message', \
                 'author__id', 'author__username')
        serializer = SubmissionSerializer(queryset, many=True)
        return Response(serializer.data)
