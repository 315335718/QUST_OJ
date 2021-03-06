from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic import TemplateView, View, ListView
from django.core.cache import cache
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.http import JsonResponse, HttpResponse
from django_q.tasks import async_task
from django.db.models import Q
from ipware.ip import get_client_ip

from account.permissions import is_problem_manager
from account.models import User
from problem.models import Problem
from contest.models import Contest
from submission.models import Submission
from problem.tasks import create_submission, judge_submission_on_problem
from account.permissions import is_admin_or_root
from problem.safe import drop_database_safe


class ProblemDetailMixin(TemplateResponseMixin, ContextMixin, UserPassesTestMixin):

    def dispatch(self, request, *args, **kwargs):
        self.problem = get_object_or_404(Problem, pk=kwargs.get('pk'))
        self.user = request.user
        self.privileged = is_problem_manager(self.user, self.problem)
        self.request = request
        return super(ProblemDetailMixin, self).dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.privileged or self.problem.visible

    def get_context_data(self, **kwargs):
        data = super(ProblemDetailMixin, self).get_context_data(**kwargs)
        data['problem'] = self.problem
        return data


class ProblemView(ProblemDetailMixin, TemplateView):
    def get_template_names(self):
        return ['problem/problem.jinja2']

    def get_stats(self):
        data = {
            'user_ac_count': self.problem.ac_user_count,
            'user_all_count': self.problem.total_user_count,
            'ac_count': self.problem.ac_count,
            'all_count': self.problem.total_count,
            'problem_type': self.problem.problem_type,
        }
        return data

    def get_context_data(self, **kwargs):
        data = super(ProblemView, self).get_context_data()
        data['problem'] = self.problem
        data['user'] = self.user
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return data


def check_try_max(contest, participant_id, problem_id):
    max_try = contest.max_try
    submissions = contest.submission_set.filter(author_id=participant_id, problem_id=problem_id)[:max_try]
    if len(submissions) >= max_try:
        return 1
    else:
        return 0


class ContestProblemDetailMixin(TemplateResponseMixin, ContextMixin, UserPassesTestMixin):

    def dispatch(self, request, *args, **kwargs):
        self.problem = get_object_or_404(Problem, pk=kwargs.get('pk'))
        self.user = request.user
        self.privileged = is_problem_manager(self.user, self.problem)
        self.request = request
        self.contest_id = kwargs.get('c_pk')
        return super(ContestProblemDetailMixin, self).dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.privileged or self.problem.visible or self.contest_id > 0

    def get_context_data(self, **kwargs):
        data = super(ContestProblemDetailMixin, self).get_context_data(**kwargs)
        data['problem'] = self.problem
        return data


class ProblemSubmitView(ContestProblemDetailMixin, View):

    def test_func(self):
        return super(ProblemSubmitView, self).test_func() and self.user.is_authenticated

    def post(self, request, *args, **kwargs):
        try:
            c_pk = self.kwargs['c_pk']
            code = request.POST.get('code', '')
            contest = None
            if int(c_pk) > 0:
                contest = Contest.objects.get(pk=c_pk)
                flag = check_try_max(contest, self.request.user.id, self.problem.id)
                if flag == 1:
                    return HttpResponseRedirect(reverse("contest:dashboard", args=(c_pk,)))
            flag = 1;
            flag &= drop_database_safe(code)
            if flag == 0:
                baned_user = User.objects.get(pk=request.user.id)
                baned_user.is_active = 0
                baned_user.username += " ???????????????????????????????????????"
                baned_user.save(update_fields=['username', 'is_active'])
                return redirect('/reject/')
            submission = create_submission(self.problem, self.user, code, contest, ip=get_client_ip(request))
            async_task(judge_submission_on_problem, submission)
            if contest is not None:
                return HttpResponseRedirect(reverse("contest:my_submissions", args=(c_pk,)))
            else:
                return HttpResponseRedirect(reverse("problem:submissions", args=(self.problem.id,)))
        except Exception as e:
            return HttpResponseBadRequest(str(e).encode())


class ProblemSubmissionsView(View):
    template_name = 'problem/problem_submissions.jinja2'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        problem_id = kwargs.get('pk')
        p = Problem.objects.get(id=problem_id)
        user = self.request.user
        queryset = user.submission_set.filter(problem_id=p.id)[:20].select_related('author'). \
            only('pk', 'create_time', 'judge_end_time', 'author__id', 'status', 'status_percent', 'status_message')
        contents = {
            'user': request.user,
            'problem': p,
            'submission_list': queryset,
        }
        return render(request, self.template_name, contents)


class AllSubmissionsView(View):
    template_name = 'problem/submissions.jinja2'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        queryset = Submission.objects.all()[:50].select_related('problem', 'author'). \
            only('pk', 'create_time', 'judge_end_time', 'author__id', 'problem__id', 'status', \
                 'status_percent', 'status_message', 'author__username', 'author__is_superuser', 'author__is_active')
        contents = {
            'submission_list': queryset,
        }
        return render(request, self.template_name, contents)


class ProblemListView(ListView):
    template_name = 'problem/problem_list.jinja2'
    paginate_by = 1000
    context_object_name = 'problem_list'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        queryset = Problem.objects.all().only('pk', 'title', 'problem_type', 'level', 'ac_count', 'total_count',
                                              'description')
        if not is_admin_or_root(self.request.user):
            queryset = queryset.filter(visible=True)
        # ret = queryset.defer('description')
        ret = queryset.order_by('id')
        return ret
