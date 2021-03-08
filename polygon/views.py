import time
import random
import re
import os

from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views.generic import View, FormView, ListView, TemplateView
from django.views.generic.base import TemplateResponseMixin, ContextMixin
from django.views.generic.edit import UpdateView
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction

from account.models import User
from contest.models import Contest, ContestParticipant
from problem.models import Problem
from schoolclass.models import SchoolClass
from polygon.forms import ProblemForm, UpdateProblemForm, CaseForm, UpdateCasesForm
from polygon.forms import UpdateContestForm
from account.permissions import is_contest_manager
from home.search_api import get_problem_q_object, sorted_query
from account.permissions import is_admin_or_root


class AddProblemView(FormView):
    template_name = 'polygon/problem/add_problem.jinja2'
    form_class = ProblemForm

    def form_valid(self, form):
        form.create()
        self.success_url = reverse("polygon:problem_list")
        return super().form_valid(form)


class ProblemListView(ListView):
    template_name = 'polygon/problem/polygon_problem_list.jinja2'
    paginate_by = 1000
    context_object_name = 'problem_list'

    def get_queryset(self):
        queryset = Problem.objects.all()
        if not is_admin_or_root(self.request.user):
            queryset = queryset.filter(visible=True)
        ret = queryset.defer("description").distinct()
        ret = ret.order_by('id')
        return ret


class UpdateProblemView(FormView):
    template_name = 'polygon/problem/update_problem.jinja2'
    form_class = UpdateProblemForm

    # success_url = 'polygon/problem_list'

    def get(self, request, *args, **kwargs):
        problem_id = self.kwargs['pk']
        p = Problem.objects.get(id=problem_id)
        form = self.form_class(instance=p)
        cur = {'form': form, 'problem_id': problem_id}
        return self.render_to_response(cur)

    def form_valid(self, form, problem_id):
        form.create(form, problem_id)
        self.success_url = reverse("polygon:problem_list")
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = UpdateProblemForm(request.POST)
        if form.is_valid():
            problem_id = kwargs.get('pk')
            return self.form_valid(form, problem_id)
        else:
            return self.form_invalid(form)


class DeleteProblemView(View):
    def get(self, request, *args, **kwargs):
        problem_id = kwargs.get('pk')
        p = Problem.objects.get(id=problem_id)
        # 删除测试用例
        this_dir = p.address
        file_list = os.listdir(this_dir)
        for f in file_list:
            file_path = os.path.join(this_dir, f)
            os.remove(file_path)
        os.removedirs(this_dir)
        Problem.objects.filter(id=problem_id).delete()
        return HttpResponseRedirect(reverse("polygon:problem_list"))


class AddCaseView(View):
    template_name = 'polygon/problem/add_case.jinja2'
    form_class = CaseForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        cur_pk = kwargs.get('pk')
        return render(request, self.template_name, {'form': form, 'cur_pk': cur_pk})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            cur_pk = kwargs.get('pk')
            p = Problem.objects.get(pk=cur_pk)
            case_list = list(filter(lambda x: x, re.split(r"[,;\[\]' ]", p.cases)))
            ticks1 = int(time.time())
            filename = p.address + '/' + str(ticks1) + str(random.randint(1, 100)) + str(
                random.randint(1, 100)) + '.txt'
            sqlcode = request.POST.get('content')
            with open(filename, 'w', encoding='utf-8') as file_object:
                file_object.write(sqlcode)
            case_list.append(filename)
            p.cases = str(case_list)
            p.case_total += 1
            p.save()
            s_url = reverse('polygon:update_cases', kwargs={'pk': cur_pk, 'case_id': p.case_total})
            return HttpResponseRedirect(s_url)

        return render(request, self.template_name, {'form': form})


class UpdateCasesView(FormView):
    template_name = 'polygon/problem/update_cases.jinja2'
    form_class = UpdateCasesForm

    def get(self, request, *args, **kwargs):
        problem_id = self.kwargs['pk']
        case_id = self.kwargs['case_id']
        p = Problem.objects.get(id=problem_id)
        case_list = list(filter(lambda x: x, re.split(r"[,;\[\]' ]", p.cases)))
        if len(case_list) == 0 or int(case_id) > len(case_list):
            s_url = reverse('polygon:add_case', kwargs={'pk': problem_id})
            return HttpResponseRedirect(s_url)
        file_name = case_list[int(case_id) - 1]
        with open(file_name, 'r') as f:
            sqlcode = f.read()
        form = self.form_class()
        form.initial['content'] = sqlcode
        all_case = list(range(1, p.case_total + 1))
        cur = {'form': form, 'problem_id': int(problem_id), 'case_ID': int(case_id), 'all_case': all_case}
        return self.render_to_response(cur)

    def form_valid(self, form, problem_id, case_id):
        form.create(form, problem_id, case_id)
        self.success_url = reverse('polygon:update_cases', kwargs={'pk': problem_id, 'case_id': case_id})
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = UpdateCasesForm(request.POST)
        if form.is_valid():
            problem_id = kwargs.get('pk')
            case_id = kwargs.get('case_id')
            return self.form_valid(form, problem_id, case_id)
        else:
            return HttpResponseRedirect('/reject/')


class DeleteCaseView(View):
    def get(self, request, *args, **kwargs):
        problem_id = self.kwargs['pk']
        case_id = self.kwargs['case_id']
        p = Problem.objects.get(id=problem_id)
        case_list = list(filter(lambda x: x, re.split(r"[,;\[\]' ]", p.cases)))
        if len(case_list) == 0 or int(case_id) > len(case_list):
            return HttpResponseRedirect('/reject/')
        filename = case_list[int(case_id) - 1]
        os.remove(filename)
        del case_list[int(case_id) - 1]
        p.cases = str(case_list)
        p.case_total -= 1
        p.save()
        s_url = reverse('polygon:update_cases', kwargs={'pk': problem_id, 'case_id': p.case_total})
        return HttpResponseRedirect(s_url)


class PolygonBaseMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser


class AddContestView(View, PolygonBaseMixin):
    def get(self, request, *args, **kwargs):
        contest = Contest.objects.create(title='Contest')
        contest.title = 'Contest #%d' % contest.id
        contest.save(update_fields=['title'])
        contest.managers.add(request.user)
        return redirect(reverse('polygon:update_contest', kwargs={'pk': contest.id}))


class PolygonContestMixin(TemplateResponseMixin, ContextMixin, PolygonBaseMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        self.contest = get_object_or_404(Contest, pk=kwargs.get('pk'))
        return super(PolygonContestMixin, self).dispatch(request, *args, **kwargs)

    def test_func(self):
        if not is_contest_manager(self.request.user, self.contest):
            return False
        return super(PolygonContestMixin, self).test_func()

    def get_context_data(self, **kwargs):
        data = super(PolygonContestMixin, self).get_context_data(**kwargs)
        data['contest'] = self.contest
        return data


class UpdateContestView(PolygonContestMixin, UpdateView):
    form_class = UpdateContestForm
    template_name = 'polygon/contest/update_contest.jinja2'
    queryset = Contest.objects.all()

    def get_context_data(self, **kwargs):
        data = super(UpdateContestView, self).get_context_data(**kwargs)
        data['admin_list'] = self.contest.managers.all()
        return data

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.save()
        # if instance.contest_type == '测试':
        #     with transaction.atomic():
        #         participants = {p.user_id: p for p in instance.contestparticipant_set.all()}
        #         for sub in instance.submission_set.all():
        #             start = participants[sub.author_id].start_time(instance)
        #             end = start + instance.length
        #             if start <= sub.create_time <= end:
        #                 sub.contest_time = sub.create_time - start
        #             else:
        #                 sub.contest_time = None
        #             sub.save(update_fields=["contest_time"])
        return redirect(reverse('polygon:contest_list'))


class ContestListView(PolygonBaseMixin, ListView):
    template_name = 'polygon/contest/polygon_contest_list.jinja2'
    context_object_name = 'contest_list'

    def get_queryset(self):
        return Contest.objects.all()


class ContestProblemView(PolygonContestMixin, TemplateView):
    template_name = 'polygon/contest/polygon_contest_problem.jinja2'

    def get(self, request, *args, **kwargs):
        kw = request.GET.get('key_word')
        results = list()
        count = 0
        if kw != '':
            managing = request.user
            q = get_problem_q_object(kw, is_admin_or_root(request.user), managing)
            if q:
                for problem in sorted_query(Problem.objects.filter(q).distinct().all(), kw):
                    results.append(dict(name=problem.pk, value=problem))
                    count += 1

        problems = self.contest.contest_problem_list
        data = []
        SUB_FIELDS = ["title", "id"]
        for problem in problems:
            d = {k: getattr(problem.problem, k) for k in SUB_FIELDS}
            d.update(pid=problem.id, identifier=problem.identifier)
            d["accept"] = str(problem.ac_user_count) + '/' + str(problem.total_user_count)
            d["solve"] = str(problem.ac_count) + '/' + str(problem.total_count)
            d["user_ratio"] = '(' + str(round(problem.user_ratio * 100, 2)) + '%)'
            d["ratio"] = '(' + str(round(problem.ratio * 100, 2)) + '%)'
            data.append(d)
        return render(request, self.template_name,
                      {'data': data, 'contest_id': self.contest.id, 'results': results, 'count': count})


def reorder_contest_problem_identifiers(contest: Contest, orders=None):
    with transaction.atomic():
        problems = list(contest.contestproblem_set.select_for_update().order_by('identifier').all())
        if orders:
            problems.sort(key=lambda x: orders[x.id])
        if len(problems) > 26:
            for index, problem in enumerate(problems, start=1):
                problem.identifier = str(1000 + index)
                problem.save(update_fields=['identifier'])
        else:
            for index, problem in enumerate(problems, start=0):
                problem.identifier = chr(ord('A') + index)
                problem.save(update_fields=['identifier'])


class ContestAddProblemView(PolygonContestMixin, View):
    def post(self, request, *args, **kwargs):
        def get_next_identifier(identifiers):
            from collections import deque
            q = deque()
            q.append('')
            while q:
                u = q.popleft()
                if u and u not in identifiers:
                    return u
                for i in range(ord('A'), ord('Z') + 1):
                    q.append(u + chr(i))

        count = request.POST.get('count')
        count = int(count)
        problems = []
        for i in range(1, count + 1):
            problems.append(request.POST.get(str(i)))
        for problem in problems:
            if self.contest.contestproblem_set.filter(problem_id=problem).exists():
                continue
            identifier = get_next_identifier([x.identifier for x in self.contest.contestproblem_set.all()])
            self.contest.contestproblem_set.create(problem_id=problem, identifier=identifier)
        reorder_contest_problem_identifiers(self.contest)
        return HttpResponseRedirect(reverse('polygon:contest_problem', args=(self.contest.id,)))


class ContestRemoveProblemView(PolygonContestMixin, View):
    def get(self, request, *args, **kwargs):
        p_pk = self.kwargs['p_pk']
        self.contest.contestproblem_set.filter(problem_id=p_pk).delete()
        reorder_contest_problem_identifiers(self.contest)
        return HttpResponseRedirect(reverse('polygon:contest_problem', args=(self.contest.id,)))


class ContestParticipantView(PolygonContestMixin, ListView):
    template_name = 'polygon/contest/polygon_contest_participant.jinja2'
    paginate_by = 100
    context_object_name = 'participant_list'

    def get_queryset(self):
        return Contest.objects.get(pk=self.kwargs.get('pk')).contestparticipant_set.select_related('user').all()

    def get_context_data(self, **kwargs):
        data = super(ContestParticipantView, self).get_context_data(**kwargs)
        data['contest'] = Contest.objects.get(pk=self.kwargs.get('pk'))
        user_id = self.request.user.id
        now_user = User.objects.get(id=user_id)
        class_list = []
        if now_user.is_superuser:
            class_list = SchoolClass.objects.filter(tercher_id=now_user.id)
        data['class_list'] = class_list
        data['contest_id'] = self.contest.id
        return data


class ContestAddOneParticipantView(PolygonContestMixin, View):
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            with transaction.atomic():
                if not self.contest.contestparticipant_set.filter(user=user).exists():
                    ContestParticipant.objects.create(user=user, contest=self.contest)
        except:
            print('该用户不存在')
        return HttpResponseRedirect(reverse('polygon:contest_participant', args=(self.contest.id, )))


class ContestAddParticipantByClassView(PolygonContestMixin, View):
    def post(self, request, *args, **kwargs):
        class_id = request.POST.get('class_id')
        try:
            users = User.objects.filter(school_class_id=class_id)
            for user in users:
                with transaction.atomic():
                    if not self.contest.contestparticipant_set.filter(user=user).exists():
                        ContestParticipant.objects.create(user=user, contest=self.contest)
        except:
            print('Wrong in ContestAddParticipantByClassView')
        return HttpResponseRedirect(reverse('polygon:contest_participant', args=(self.contest.id, )))


class ContestRemoveUserView(PolygonContestMixin, View):
    def get(self, request, *args, **kwargs):
        u_pk = self.kwargs['u_pk']
        self.contest.contestparticipant_set.filter(user_id=u_pk).delete()
        return HttpResponseRedirect(reverse('polygon:contest_participant', args=(self.contest.id, )))


class ContestRemoveUserView(PolygonContestMixin, View):
    def get(self, request, *args, **kwargs):
        u_pk = self.kwargs['u_pk']
        self.contest.contestparticipant_set.filter(user_id=u_pk).delete()
        return HttpResponseRedirect(reverse('polygon:contest_participant', args=(self.contest.id, )))