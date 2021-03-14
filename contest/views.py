import xlwt
import time
import random
import os

from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, View
from django import forms
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils import timezone
from django.utils.encoding import escape_uri_path

from QUST_OJ.settings import EXCEL_ROOT
from contest.models import Contest, ContestParticipant
from problem.models import Problem
from submission.models import Submission
from account.permissions import is_admin_or_root


class ContestListView(ListView):
    template_name = 'contest/contest_list.jinja2'
    paginate_by = 1000
    context_object_name = 'contest_list'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        user = self.request.user if self.request.user.is_authenticated else None
        return Contest.objects.get_status_list(show_all=is_admin_or_root(self.request.user), filter_user=user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["hide_header"] = True
        return data


class InvitationCodeForm(forms.Form):
    content = forms.CharField(label='邀请码')


class InvitationCodeInputView(View):
    template_name = 'contest/invitation_code_input.jinja2'
    form_class = InvitationCodeForm

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            pk = kwargs.get('pk')
            contest = Contest.objects.get(pk=pk)
            user_input = form.cleaned_data['content']
            if user_input == contest.invitation_code:
                ContestParticipant.objects.create(user=self.request.user, contest=contest)
                return HttpResponseRedirect(reverse('contest:dashboard', args=(contest.id,)))
            else:
                return HttpResponseRedirect(reverse('contest:list'))


class DashboardView(View):
    template_name = 'contest/dashboard.jinja2'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        pk = self.kwargs['pk']
        contest = Contest.objects.get(id=pk)
        if contest.status == -1:
            redirect(reverse('contest:list'))
        contest_participant = contest.contestparticipant_set.all()
        participant_id = self.request.user.id
        flag = contest_participant.filter(user_id=participant_id).exists()
        if not flag:
            if is_admin_or_root(self.request.user) or contest.access_level == 20:
                ContestParticipant.objects.create(user=self.request.user, contest=contest)
            elif contest.access_level == 10:
                return redirect(reverse('contest:invitation_code', args=(contest.id,)))
            else:
                return redirect('/reject/')
        contest_problem = contest.contestproblem_set.all()
        problems = []
        for it in contest_problem:
            problems.append(it.problem)
        submissions = contest.submission_set.all()
        result = []
        for problem in problems:
            one = dict()
            one['id'] = problem.id
            one['title'] = problem.title
            count = 0
            for it in contest_participant:
                user = it.user
                for submission in submissions:
                    if submission.author_id == user.id and submission.problem_id == problem.id and submission.status_percent > 99.9:
                        count += 1
                        break
            one['total'] = count
            result.append(one)
        now = timezone.now()
        problem_score = 0
        if contest.status == 0:
            problem_score = round(60 + 40 * (contest.end_time - now) / contest.length, 2)
        return render(request, self.template_name,
                      {'result': result, 'contest': contest, 'problem_score': problem_score})


class ContestProblemView(View):
    template_name = 'contest/contest_problem.jinja2'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        pk = self.kwargs['pk']
        p_pk = self.kwargs['p_pk']
        contest = Contest.objects.get(pk=pk)
        if contest.status == -1:
            redirect(reverse('contest:list'))
        problem = Problem.objects.get(pk=p_pk)
        now = timezone.now()
        if now > contest.end_time:
            return HttpResponseRedirect(reverse("contest:dashboard", args=(pk,)))
        # contest_participant = contest.contestparticipant_set.all()
        # participant_id = self.request.user.id
        # if not contest_participant.filter(user_id=participant_id).exists():
        #     redirect('/reject/')
        return render(request, self.template_name, {'contest': contest, 'problem': problem})


class ContestMySubmissionsView(View):
    template_name = 'contest/contest_submissions.jinja2'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        pk = self.kwargs['pk']
        contest = Contest.objects.get(pk=pk)
        if contest.status == -1:
            redirect(reverse('contest:list'))
        # contest_participant = contest.contestparticipant_set.all()
        # participant_id = self.request.user.id
        # if not contest_participant.filter(user_id=participant_id).exists():
        #     redirect('/reject/')
        queryset = Submission.objects.filter(Q(author_id=request.user.id) & Q(contest_id=pk))
        contents = {
            'flag': 1,
            'user': request.user,
            'contest': contest,
            'submission_list': queryset,
        }
        return render(request, self.template_name, contents)


class ContestSubmissionsView(View):
    template_name = 'contest/contest_submissions.jinja2'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        pk = self.kwargs['pk']
        contest = Contest.objects.get(pk=pk)
        if contest.status == -1:
            redirect(reverse('contest:list'))
        queryset = Submission.objects.filter(Q(contest_id=pk))
        contents = {
            'flag': 0,
            'contest': contest,
            'submission_list': queryset,
        }
        return render(request, self.template_name, contents)


class StandingsView(View):
    template_name = 'contest/standings.jinja2'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        pk = self.kwargs['pk']
        contest = Contest.objects.get(id=pk)
        if contest.status == -1:
            redirect(reverse('contest:list'))
        contest_participant = contest.contestparticipant_set.all()
        contest_problem = contest.contestproblem_set.all()
        submissions = contest.submission_set.all()
        result = []
        for it in contest_participant:
            participant = it.user
            one = dict()
            one['user'] = participant
            one['score'] = 0
            one['total'] = 0
            for ij in contest_problem:
                problem = ij.problem
                max_score = 0
                sum_score = 0
                flag = 0
                count = 0
                for submission in submissions:
                    if submission.author_id == participant.id and submission.problem_id == problem.id:
                        count += 1
                        if submission.status_percent > 99.9:
                            flag = 1
                        time_score = 100
                        if contest.is_time_score:
                            time_score = 100 * ((contest.end_time - submission.create_time) / contest.length)
                        now_score = submission.status_percent * 0.6 + submission.status_percent * 0.4 * time_score / 100
                        if now_score > max_score:
                            max_score = now_score
                        sum_score += now_score
                if contest.is_best_counts:
                    one['score'] += max_score
                else:
                    if count != 0:
                        one['score'] += sum_score / count
                if flag:
                    one['total'] += 1
            result.append(one)
        result.sort(key=lambda x: x['score'], reverse=True)
        return render(request, self.template_name, {'result': result, 'contest': contest, 'user': self.request.user})


class OutputStandingsToExcelView(View):

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        pk = self.kwargs['pk']
        contest = Contest.objects.get(id=pk)
        if contest.status == -1:
            redirect(reverse('contest:list'))
        contest_participant = contest.contestparticipant_set.all()
        contest_problem = contest.contestproblem_set.all()
        submissions = contest.submission_set.all()
        result = []
        for it in contest_participant:
            participant = it.user
            one = dict()
            one['user'] = participant
            one['score'] = 0
            one['total'] = 0
            for ij in contest_problem:
                problem = ij.problem
                max_score = 0
                sum_score = 0
                flag = 0
                count = 0
                for submission in submissions:
                    if submission.author_id == participant.id and submission.problem_id == problem.id:
                        count += 1
                        if submission.status_percent > 99.9:
                            flag = 1
                        time_score = 100
                        if contest.is_time_score:
                            time_score = 100 * ((contest.end_time - submission.create_time) / contest.length)
                        now_score = submission.status_percent * time_score / 100
                        if now_score > max_score:
                            max_score = now_score
                        sum_score += now_score
                if contest.is_best_counts:
                    one['score'] += max_score
                else:
                    if count != 0:
                        one['score'] += sum_score / count
                if flag:
                    one['total'] += 1
            result.append(one)
        result.sort(key=lambda x: x['score'], reverse=True)

        data = xlwt.Workbook(encoding='utf-8')
        sheet = data.add_sheet('sheet1', cell_overwrite_ok=True)
        sheet.write(0, 0, "学号")
        sheet.write(0, 1, "姓名")
        sheet.write(0, 2, "做对题数")
        sheet.write(0, 3, "最终成绩")
        thisrow = 1
        for ele in result:
            sheet.write(thisrow, 0, ele['user'].username)
            sheet.write(thisrow, 1, ele['user'].name)
            sheet.write(thisrow, 2, ele['total'])
            sheet.write(thisrow, 3, ele['score'])
            thisrow += 1

        ticks = int(time.time())
        excel_dir = str(EXCEL_ROOT)

        del_list = os.listdir(excel_dir)
        for f in del_list:
            file_path = os.path.join(excel_dir, f)
            os.remove(file_path)

        excel_file = excel_dir + '/' + str(ticks) + str(random.randint(1, 100)) + str(random.randint(1, 100)) + '.xls'
        data.save(excel_file)

        with open(excel_file, 'rb') as f:
            try:
                download_name = contest.title + '____榜单.xls'
                response = HttpResponse(f)
                response['content_type'] = "application/octet-stream"
                response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(download_name))
                return response
            except Exception:
                raise Http404
