from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Q
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from submission.models import Submission


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = "__all__"


class GetAllSubmissionView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Submission.objects.all()[:50].select_related('problem', 'author'). \
            only('pk', 'create_time', 'judge_end_time', 'author_id', 'problem_id', 'status', 'status_percent', 'status_message')
        serializer = SubmissionSerializer(queryset, many=True)
        return Response(serializer.data)


class GetOneProblemSubmissionView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['u_id']
        problem_id = self.kwargs['p_id']
        queryset = Submission.objects.filter(Q(author_id=user_id) & Q(problem_id=problem_id) & Q(contest_id=None))[:5]
        serializer = SubmissionSerializer(queryset, many=True)
        return Response(serializer.data)
