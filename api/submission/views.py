from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from ipware.ip import get_client_ip
from django_q.tasks import async_task

from problem.models import Problem
from problem.safe import drop_database_safe
from account.models import User
from problem.views import check_try_max
from contest.models import Contest
from submission.models import Submission
from submission.utils import SubmissionStatus
from problem.tasks import judge_submission_on_problem


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ('id', 'title')


class SubmissionSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer()
    class Meta:
        model = Submission
        fields = ('id', 'code', 'create_time', 'judge_end_time', 'status', 'status_percent', 'status_message', \
                  'running_process', 'author', 'problem', 'contest')


class MySubmissionsView(APIView):
    # permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            user_id = request.GET.get('user_id', 0)
            if int(user_id) == 0:
                return Response({'flag': 0, 'message': '检查是否登录或网络连接是否正常'})  # 检查是否未登录
            user = User.objects.get(pk=user_id)
            submissions = user.submission_set.all()[:20].select_related('problem', 'author')
            serializer = SubmissionSerializer(submissions, many=True)
            contents = {
                'flag': 1,
                'submission_list': serializer.data,
                'message': '正常访问',
            }
            print(contents)
            return Response(contents)
        except Exception as e:
            return Response({'flag': 0, 'message': '系统错误: ' + str(str(e).encode())})