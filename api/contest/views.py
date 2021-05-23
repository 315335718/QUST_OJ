from rest_framework.views import APIView
from rest_framework.response import Response

from account.models import User
from account.permissions import is_admin_or_root
from contest.models import Contest, ContestParticipant
from contest.views import get_problem_score
from api.problem.views import ProblemSerializer


class ContestListView(APIView):
    # permission_classes = (IsAuthenticated,)
    def get(self, request):
        user_id = request.GET.get('user_id', 0)
        if int(user_id) == 0:
            return Response({'flag': 0, 'message': '检查是否登录或网络连接是否正常'})  # 检查是否未登录
        user = User.objects.get(pk=user_id)
        res = Contest.objects.get_status_list(show_all=is_admin_or_root(self.request.user), filter_user=user)
        contest_list = []
        for it in res:
            one = dict()
            one['id'] = it.id
            one['title'] = it.title
            one['description'] = it.description
            one['contest_type'] = it.contest_type
            one['start_time'] = it.start_time
            one['end_time'] = it.end_time
            one['is_best_counts'] = it.is_best_counts
            one['is_time_score'] = it.is_time_score
            one['time_score_wait'] = it.time_score_wait
            one['max_try'] = it.max_try
            one['access_level'] = it.access_level
            one['status'] = it.status
            contest_list.append(one)
        return Response({'flag': 1, 'contest_list': contest_list})


class ContestDashboardView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id', 0)
        cid = request.GET.get('cid', 0)
        if int(user_id) == 0 or int(cid) == 0:
            return Response({'flag': 0, 'message': '检查是否登录或网络连接是否正常'})  # 检查是否未登录
        contest = Contest.objects.get(id=cid)
        try:
            user = User.objects.get(pk=user_id)
        except Exception as e:
            return Response({'flag': 0, 'message': '系统错误: ' + str(str(e).encode())})
        if not user.is_superuser and contest.status < 0:
            return Response({'flag': 0, 'message': '测试未开始'})
        contest_participant = contest.contestparticipant_set.all().select_related('contest', 'user')
        participant_id = user.id
        flag = contest_participant.filter(user_id=participant_id).exists()
        if not flag:
            if is_admin_or_root(user) or contest.access_level == 20:
                ContestParticipant.objects.create(user=user, contest=contest)
            else:
                return Response({'flag': 0, 'message': '无权限访问'})
        contest_problem = contest.contestproblem_set.all().select_related('contest', 'problem')
        problem_list = []
        for it in contest_problem:
            problem_list.append(it.problem)
        serializer = ProblemSerializer(problem_list, many=True)
        problem_score = get_problem_score(contest)
        return Response({'flag': 1, 'message': '正常访问', 'problem_list': serializer.data, 'problem_score': problem_score, \
                         'status': contest.status})