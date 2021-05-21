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
        fields = ("id", "title", "description", "problem_type", "level", "ac_count", "total_count")


class ProblemListView(APIView):
    # permission_classes = (IsAuthenticated,)
    def get(self, request):
        print(request.GET.get('mname', 'world'))
        problem_list = Problem.objects.all().only('id', 'title', 'description', 'problem_type', 'level', 'ac_count', \
                                                  'total_count').order_by('id')
        serializer = ProblemSerializer(problem_list, many=True)
        return Response({'problem_list': serializer.data})


class ProblemView(APIView):
    # permission_classes = (IsAuthenticated,)
    def get(self, request):
        id = request.GET.get('pid', 1)
        problem = Problem.objects.get(pk=id)
        serializer = ProblemSerializer(problem)
        return Response({'problem': serializer.data})


class ProblemSubmitView(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            user_id = request.POST.get('user_id', 0)
            cid = request.POST.get('cid', 0)
            pid = request.POST.get('pid', 0)
            code = request.POST.get('code', '')
            print(user_id, cid, pid, code)
            if int(user_id) == 0 or int(pid) == 0:
                return Response({'flag': 0, 'message': '检查是否登录或网络连接是否正常'})  # 检查是否未登录
            author = User.objects.get(pk=user_id)
            problem = Problem.objects.get(pk=pid)
            contest = None
            if int(cid) > 0:
                contest = Contest.objects.get(pk=cid)
                flag = check_try_max(contest, user_id, pid)
                if flag == 1:
                    return Response({'flag': 0, 'message': '测试中本题超过最大提交次数'})  # 在测试中超过最大提交次数
            flag = 1
            flag &= drop_database_safe(code)
            if flag == 0:
                baned_user = User.objects.get(user_id)
                baned_user.is_active = 0
                baned_user.username += " 被检测为恶意用户，已被封禁"
                baned_user.save(update_fields=['username', 'is_active'])
                return Response({'flag': 0, 'message': '检测到恶意代码，您已被封禁'})  # 检测到恶意代码，封禁该用户
            if not 6 <= len(code) <= 65536:
                return Response({'flag': 0, 'message': '代码不得小于 6 字节，不得超过 65536 字节。'})
            if author.submission_set.exists() and (
                    datetime.now() - author.submission_set.first().create_time).total_seconds() < 5:
                return Response({'flag': 0, 'message': '5 秒内只能提交一次。'})
            problem.total_count += 1
            problem.save(update_fields=['total_count'])
            submission = Submission.objects.create(code=code, author=author, problem=problem, contest=contest,
                                                   status=SubmissionStatus.WAITING, ip=get_client_ip(request),
                                                   visible=True)
            async_task(judge_submission_on_problem, submission)
            if contest is not None:
                return Response({'flag': 2, 'message': '正常提交'})
            else:
                return Response({'flag': 1, 'message': '正常提交'})
        except Exception as e:
            return Response({'flag': 0, 'message': '系统错误: ' + str(str(e).encode())})
