import re
import xlwt
import time
import random
import os
from datetime import timedelta

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


def get_problem_score(contest):
    now = timezone.now()
    problem_score = 0
    time_score = 100
    time_score_delta = timedelta(minutes=contest.time_score_wait)
    if contest.is_time_score:
        time_delta = now - contest.start_time
        if time_delta > time_score_delta and contest.length != time_score_delta:
            time_score = 100 * ((contest.end_time - now) / (contest.length - time_score_delta))
    if contest.status == 0:
        problem_score = round(60 + 40 * time_score / 100, 2)
    return problem_score


class DashboardView(View):
    template_name = 'contest/dashboard.jinja2'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        pk = self.kwargs['pk']
        contest = Contest.objects.get(id=pk)
        if not request.user.is_superuser and contest.status < 0:
            return redirect(reverse('contest:list'))
        contest_participant = contest.contestparticipant_set.all().select_related('contest', 'user'). \
            only('user__id', 'contest__id')
        participant_id = self.request.user.id
        flag = contest_participant.filter(user_id=participant_id).exists()
        if not flag:
            if is_admin_or_root(self.request.user) or contest.access_level == 20:
                ContestParticipant.objects.create(user=self.request.user, contest=contest)
            elif contest.access_level == 10:
                return redirect(reverse('contest:invitation_code', args=(contest.id,)))
            else:
                return redirect('/reject/')
        contest_problem = contest.contestproblem_set.all().select_related('contest', 'problem'). \
            only('problem__id', 'problem__title', 'contest__id')
        problems = []
        for it in contest_problem:
            problems.append(it.problem)
        result = []
        for problem in problems:
            one = dict()
            one['id'] = problem.id
            one['title'] = problem.title
            result.append(one)
        problem_score = get_problem_score(contest)
        return render(request, self.template_name,
                      {'result': result, 'contest': contest, 'problem_score': problem_score})


class ContestProblemView(View):
    template_name = 'contest/contest_problem.jinja2'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        pk = self.kwargs['pk']
        p_pk = self.kwargs['p_pk']
        idx = request.GET.get('index', 1)
        contest = Contest.objects.get(pk=pk)
        if not request.user.is_superuser and contest.status < 0:
            return redirect(reverse('contest:list'))
        problem = Problem.objects.get(pk=p_pk)
        now = timezone.now()
        if now > contest.end_time:
            return HttpResponseRedirect(reverse("contest:dashboard", args=(pk,)))
        contest_participant = contest.contestparticipant_set.all()
        participant_id = self.request.user.id
        if not contest_participant.filter(user_id=participant_id).exists():
            redirect('/reject/')
        problem_score = get_problem_score(contest)
        contest_problem = contest.contestproblem_set.all().select_related('contest', 'problem'). \
            only('problem__id', 'problem__title', 'contest__id')
        problems = []
        for it in contest_problem:
            problems.append(it.problem)
        result = []
        for p in problems:
            one = dict()
            one['id'] = p.id
            one['title'] = p.title
            result.append(one)
        return render(request, self.template_name, {'contest': contest, 'problem': problem, 'idx': idx, \
                                                    'problem_score': problem_score, 'result': result})


class ContestMySubmissionsView(View):
    template_name = 'contest/contest_submissions.jinja2'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        pk = self.kwargs['pk']
        contest = Contest.objects.get(pk=pk)
        if not request.user.is_superuser and contest.status < 0:
            return redirect(reverse('contest:list'))
        # contest_participant = contest.contestparticipant_set.all()
        # participant_id = self.request.user.id
        # if not contest_participant.filter(user_id=participant_id).exists():
        #     redirect('/reject/')
        user = self.request.user
        queryset = user.submission_set.filter(contest_id=pk)[:30].select_related('contest', 'problem', 'author'). \
            only('contest_id', 'problem_id', 'author_id', 'create_time', 'code', 'status', 'status_percent', \
                 'contest__time_score_wait', 'contest__is_time_score', 'contest__start_time', 'contest__end_time', \
                 'judge_end_time', 'status_message', 'problem__title', 'author__username')
        problem_score = get_problem_score(contest)
        contents = {
            'flag': 1,
            'user': request.user,
            'contest': contest,
            'submission_list': queryset,
            'problem_score': problem_score,
        }
        return render(request, self.template_name, contents)


class ContestSubmissionsView(View):
    template_name = 'contest/contest_submissions.jinja2'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        pk = self.kwargs['pk']
        contest = Contest.objects.get(pk=pk)
        if not request.user.is_superuser and contest.status < 0:
            return redirect(reverse('contest:list'))
        queryset = contest.submission_set.all()[:50].select_related('contest', 'problem', 'author'). \
            only('contest_id', 'problem_id', 'author_id', 'create_time', 'code', 'status', 'status_percent', \
                 'contest__time_score_wait', 'contest__is_time_score', 'contest__start_time', 'contest__end_time', \
                 'judge_end_time', 'status_message', 'problem__title', 'author__username')
        problem_score = get_problem_score(contest)
        contents = {
            'flag': 0,
            'contest': contest,
            'submission_list': queryset,
            'problem_score': problem_score,
        }
        return render(request, self.template_name, contents)


class CreateStandingsAndVisualizationView(View):
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        pk = self.kwargs['pk']
        contest = Contest.objects.get(id=pk)
        if not request.user.is_superuser:
            return redirect(reverse('contest:list'))
        contest_participant = contest.contestparticipant_set.all().select_related('contest', 'user'). \
            only('user__id', 'user__username', 'user__name', 'contest__id')
        contest_problem = contest.contestproblem_set.all().select_related('contest', 'problem'). \
            only('problem__id', 'problem__title', 'contest__id')
        submissions = contest.submission_set.all().select_related('contest', 'problem', 'author'). \
            only('contest_id', 'problem_id', 'author_id', 'create_time', 'code', 'status', 'status_percent', \
                 'contest__time_score_wait', 'contest__is_time_score', 'contest__start_time', 'contest__end_time', \
                 'problem__title', 'author__username').order_by('create_time')
        '''
        榜单
        '''
        max_id = 0  # 问题的最大id
        index = []  # 有效数组下标
        for it in contest_problem:
            max_id = max(max_id, it.problem.id)
            index.append(it.problem.id)
        max_id += 1
        rank = dict()
        for it in contest_participant:
            problem_score = [0] * max_id
            problem_ac = [0] * max_id
            total_score = 0
            total_ac = 0
            submit_count = [0] * max_id
            time_penalty = [0] * max_id
            one = [problem_score, problem_ac, total_score, total_ac, submit_count, time_penalty]
            rank[it.user_id] = one
        st = contest.start_time  # 测试开始时间
        ed = contest.end_time  # 测试结束时间
        p = 0
        # 可视化分析所需数组
        correct_count = max_id * [0]
        has_correct_count = max_id * [0]
        compile_error_count = max_id * [0]
        incorrect_count = max_id * [0]
        all_count = max_id * [0]
        sum_score = max_id * [0]
        pro_name = max_id * [0]
        ok_submissions = []
        code_length = []
        for i in range(max_id):
            curr = dict()
            curr[-1] = 0
            code_length.append(curr)
        # code_length = [dict()] * max_id  # 直接用空字典不行，需要用一个有值的字典
        for i in range(max_id + 1):
            ok_submissions.append([])
        for it in submissions:
            if it.create_time < st or it.create_time > ed:
                p += 1  # 可视化下标
                continue
            uid = it.author_id
            pid = it.problem_id
            rank[uid][4][pid] += 1
            if it.status_percent > 99.9:
                if rank[uid][1][pid] == 0:
                    rank[uid][3] += 1
                    rank[uid][1][pid] = 1
            time_score = 100
            time_score_delta = timedelta(minutes=contest.time_score_wait)
            if contest.is_time_score:
                time_delta = it.create_time - contest.start_time
                if time_delta > time_score_delta and contest.length != time_score_delta:
                    time_score = 100 * ((contest.end_time - it.create_time) / (contest.length - time_score_delta))
            new_score = it.status_percent * 0.6 + it.status_percent * 0.4 * time_score / 100
            old_score = rank[uid][0][pid]
            if new_score > old_score:
                rank[uid][0][pid] = new_score
                rank[uid][5][pid] = it.status_percent - new_score
                rank[uid][2] += new_score - old_score

            # 可视化分析
            all_count[pid] += 1
            if it.status_percent >= 99.99:
                correct_count[pid] += 1
                cur_length = len(it.code)
                # 统计代码长度数量
                if cur_length not in code_length[pid]:
                    code_length[pid][cur_length] = 0
                code_length[pid][cur_length] += 1
                ok_submissions[pid].append(cur_length)  # 满分的加到每个题目的submission
                sum_score[pid] += it.status_percent
            elif it.status_percent > 0:
                has_correct_count[pid] += 1
                sum_score[pid] += it.status_percent
            elif it.status == 2:
                compile_error_count[pid] += 1
            else:
                incorrect_count[pid] += 1

        rank_list = []
        for it in contest_participant:
            cur = rank[it.user_id]
            problem_score = []
            problem_ac = []
            submit_count = []
            total_score = cur[2]
            total_ac = cur[3]
            time_penalty = []
            for i in index:
                problem_score.append(cur[0][i])
                problem_ac.append(cur[1][i])
                submit_count.append(cur[4][i])
                time_penalty.append(cur[5][i])
            user = [it.user.username, it.user.name, it.user_id]
            one = [user, total_ac, total_score, problem_score, submit_count, time_penalty, problem_ac]
            rank_list.append(one)
        rank_list.sort(key=lambda x: x[2], reverse=True)
        contest.standings = str(rank_list)
        '''
        可视化分析
        '''
        # 流量峰值图数据处理
        length1 = contest.length.seconds
        step1 = 10
        n1 = int(length1 / step1)
        end_time = ed
        cur_time = st
        times = []
        delta = timedelta(seconds=step1)
        submissions_len = len(submissions)
        while cur_time <= end_time:
            right_time = cur_time + delta
            if p < submissions_len and cur_time <= submissions[p].create_time <= right_time:
                cnt = 0
                while p < submissions_len and cur_time <= submissions[p].create_time <= right_time:
                    cnt += 1
                    p += 1
                times.append(cnt)
            else:
                times.append(0)
            cur_time = right_time
        # 提交信息折线柱状图、评测状态饼状图
        for it in contest_problem:
            pro_name[it.problem_id] = str(it.problem_id) + "." + it.problem.title

        correct_submission = []  # 答案正确提交数量
        has_correct_submission = []  # 部分正确提交数量
        compile_error_submission = []  # 编译错误提交数量
        incorrect_submission = []  # 完全错误提交数量
        all_submission = []  # 所有提交数量
        average_score = []  # 平均分
        correct_radio = []  # 正确率
        problem_name = []  # 题目名称
        code_length_data = []  # 代码长度数据
        scatter_chart_problem_id = []  # 散点图问题id

        max_submission_times = 0
        scatter_chart_id = 0
        for i in index:
            scatter_chart_problem_id.append("pro." + str(i))
            all_submission.append(all_count[i])
            correct_submission.append(correct_count[i])
            has_correct_submission.append(has_correct_count[i])
            compile_error_submission.append(compile_error_count[i])
            incorrect_submission.append(incorrect_count[i])
            max_submission_times = max(max_submission_times, all_count[i])
            if all_count[i] != 0:
                average_score.append(round(sum_score[i] / all_count[i], 3))
                correct_radio.append(round(correct_count[i] / all_count[i] * 100, 4))
            else:
                average_score.append(0)
                correct_radio.append(0)
            if len(pro_name[i]) > 15:
                problem_name.append(pro_name[i][:15] + "...")
            else:
                problem_name.append(pro_name[i])
            # 处理代码长度散点图
            ok_submissions[i].sort()
            s_len = len(ok_submissions[i])
            max_code_len_cnt = max(code_length[i].values())
            min_code_len_cnt = min(code_length[i].values())
            k = 0
            j = 0
            while j < s_len:
                while k < ok_submissions[i][j]:
                    k += 1
                len_cnt = 0
                while j < s_len and k == ok_submissions[i][j]:
                    len_cnt += 1
                    j += 1
                now_data = []
                now_data.append(scatter_chart_id)
                now_data.append(k)
                if all_count[i] != 0:
                    low_size = 18
                    size_len = 48
                    size = int(
                        low_size + (len_cnt - min_code_len_cnt) / (max_code_len_cnt - min_code_len_cnt) * size_len)
                    now_data.append(size)
                else:
                    now_data.append(0)
                code_length_data.append(now_data)
            scatter_chart_id += 1

        max_submission_times += int(max_submission_times * 0.36)
        # 评测状态饼状图
        pie_chart_problem = ['问题'] + problem_name
        pie_chart_correct = ['完全正确'] + correct_submission
        pie_chart_has_correct = ['部分正确'] + has_correct_submission
        pie_chart_incorrect = ['完全错误'] + incorrect_submission
        pie_chart_compile_error = ['编译错误'] + compile_error_submission
        all_pie_chart = [pie_chart_problem, pie_chart_correct, pie_chart_has_correct, pie_chart_compile_error, \
                         pie_chart_incorrect]

        data = [times, 'contest', n1, length1, step1, 'start_time', correct_submission, all_submission, average_score, \
                correct_radio, problem_name, max_submission_times, all_pie_chart, code_length_data,
                scatter_chart_problem_id]
        contest.visualization = str(data)
        contest.save(update_fields=['standings', 'visualization'])
        return redirect(reverse('contest:standings', kwargs={'pk': contest.id}))


class StandingsView(View):
    template_name = 'contest/standings.jinja2'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        pk = self.kwargs['pk']
        contest = Contest.objects.get(id=pk)
        if not request.user.is_superuser and contest.status != 1:
            return redirect(reverse('contest:list'))
        contest_problem = contest.contestproblem_set.all()
        n = len(contest_problem)
        index = n * [1]
        if len(contest.standings) < 5:
            return redirect(reverse('contest:list'))
        rank_list = eval(contest.standings)
        problem_score = get_problem_score(contest)
        width = n * 120 + 570
        return render(request, self.template_name,
                      {'rank_list': rank_list, 'contest': contest, 'user': self.request.user, 'index': index, \
                       'problem_score': problem_score, 'width': width, 'user_id': self.request.user.id, \
                       'flag': self.request.user.is_superuser})


'''导出榜单'''


class OutputStandingsToExcelView(View):

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        pk = self.kwargs['pk']
        contest = Contest.objects.get(id=pk)
        if not request.user.is_superuser:
            return redirect(reverse('contest:list'))
        contest_participant = contest.contestparticipant_set.all().select_related('contest', 'user'). \
            only('user__id', 'user__username', 'user__name', 'contest__id')
        contest_problem = contest.contestproblem_set.all().select_related('contest', 'problem'). \
            only('problem__id', 'problem__title', 'contest__id')
        submissions = contest.submission_set.all().select_related('contest', 'problem', 'author'). \
            only('contest_id', 'problem_id', 'author_id', 'create_time', 'code', 'status', 'status_percent', \
                 'contest__time_score_wait', 'contest__is_time_score', 'contest__start_time', 'contest__end_time', \
                 'problem__title', 'author__username').order_by('create_time')
        '''
        榜单
        '''
        max_id = 0  # 问题的最大id
        index = []  # 有效数组下标
        for it in contest_problem:
            max_id = max(max_id, it.problem.id)
            index.append(it.problem.id)
        max_id += 1
        rank = dict()
        for it in contest_participant:
            problem_score = [0] * max_id
            problem_ac = [0] * max_id
            total_score = 0
            total_ac = 0
            submit_count = [0] * max_id
            time_penalty = [0] * max_id
            score_code = [""] * max_id  # 最高分代码
            one = [problem_score, problem_ac, total_score, total_ac, submit_count, time_penalty, score_code]
            rank[it.user_id] = one
        st = contest.start_time  # 测试开始时间
        ed = contest.end_time  # 测试结束时间

        for it in submissions:
            if it.create_time < st or it.create_time > ed:
                continue
            uid = it.author_id
            pid = it.problem_id
            rank[uid][4][pid] += 1
            if it.status_percent > 99.9:
                if rank[uid][1][pid] == 0:
                    rank[uid][3] += 1
                    rank[uid][1][pid] = 1
            time_score = 100
            time_score_delta = timedelta(minutes=contest.time_score_wait)
            if contest.is_time_score:
                time_delta = it.create_time - contest.start_time
                if time_delta > time_score_delta and contest.length != time_score_delta:
                    time_score = 100 * ((contest.end_time - it.create_time) / (contest.length - time_score_delta))
            new_score = it.status_percent * 0.6 + it.status_percent * 0.4 * time_score / 100
            old_score = rank[uid][0][pid]
            if new_score > old_score:
                rank[uid][0][pid] = new_score
                rank[uid][5][pid] = it.status_percent - new_score
                rank[uid][2] += new_score - old_score
                rank[uid][6][pid] = it.code

        rank_list = []
        for it in contest_participant:
            cur = rank[it.user_id]
            problem_score = []
            problem_ac = []
            submit_count = []
            total_score = cur[2]
            total_ac = cur[3]
            time_penalty = []
            score_code = []
            for i in index:
                problem_score.append(cur[0][i])
                problem_ac.append(cur[1][i])
                submit_count.append(cur[4][i])
                time_penalty.append(cur[5][i])
                score_code.append(cur[6][i])
            user = [it.user.username, it.user.name, it.user_id]
            one = [user, total_ac, total_score, problem_score, submit_count, time_penalty, problem_ac, score_code]
            rank_list.append(one)
        rank_list.sort(key=lambda x: x[0][0], reverse=True)

        data = xlwt.Workbook(encoding='utf-8')
        sheet = data.add_sheet('sheet1', cell_overwrite_ok=True)

        # 单元格格式
        alignment = xlwt.Alignment()  # Create Alignment
        # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        # May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
        alignment.vert = xlwt.Alignment.VERT_CENTER
        alignment.wrap = 1  # 自动换行
        style = xlwt.XFStyle()  # Create Style
        style.alignment = alignment  # Add Alignment to Style

        alignment2 = xlwt.Alignment()  # Create Alignment
        # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
        alignment2.horz = xlwt.Alignment.HORZ_LEFT
        # May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
        alignment2.vert = xlwt.Alignment.VERT_CENTER
        alignment2.wrap = 1  # 自动换行
        style2 = xlwt.XFStyle()  # Create Style
        style2.alignment = alignment2  # Add Alignment to Style

        sheet.col(0).width = 2000
        sheet.col(1).width = 4000
        sheet.col(2).width = 4000
        sheet.col(3).width = 2000
        sheet.col(4).width = 2000
        sheet.write(0, 0, "排名", style)
        sheet.write(0, 1, "用户名", style)
        sheet.write(0, 2, "姓名", style)
        sheet.write(0, 3, "满分题数", style)
        sheet.write(0, 4, "总分", style)
        sheet.write(0, 5, "总分(百分制)", style)

        problem_num = len(contest_problem) + 1
        for i in range(1, problem_num):
            sheet.col(i + 5).width = 7777
            sheet.write(0, i + 5, "题目{0}".format(i), style)
        thisrow = 1
        for ele in rank_list:
            sheet.write(thisrow, 0, '***', style)
            sheet.write(thisrow, 1, ele[0][0], style)
            if ele[0][1] != None:
                sheet.write(thisrow, 2, ele[0][1], style)
            else:
                sheet.write(thisrow, 2, "无", style)
            sheet.write(thisrow, 3, ele[1], style)
            sheet.write(thisrow, 4, round(ele[2], 2), style)
            sheet.write(thisrow, 5, round(ele[2] / (problem_num - 1), 2), style)
            idx = 0
            for detail in ele[3]:
                info = "时间衰减后得分: {2} - {3} = {0}\n尝试次数: {1}\n最高分代码: ({4})".format(round(detail, 2),
                                                                                  ele[4][idx],
                                                                                  round(detail + ele[5][idx], 1),
                                                                                  round(ele[5][idx], 1),
                                                                                  ele[7][idx])
                sheet.write(thisrow, idx + 6, info, style2)
                idx += 1
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
                response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(
                    escape_uri_path(download_name))
                return response
            except Exception:
                raise Http404


class MergeOutputForm(forms.Form):
    content = forms.CharField(label='请输入测试的id，例如输入: 1,3,4，则合并id为 1、3、4 的成绩，注：逗号为英文逗号')


'''导出合并多个测试的榜单'''
class OutputMergedStandingsToExcelView(View):
    template_name = 'contest/merge_output.jinja2'
    form_class = MergeOutputForm

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('/')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        require = []
        if form.is_valid():
            user_input = form.cleaned_data['content']
            require = list(filter(lambda x: x, re.split(r"[, ]", user_input)))
        if require == []:
            return HttpResponseRedirect(reverse('contest:list'))
        contest = []
        for id in require:
            try:
                contest.append(Contest.objects.get(pk=id))
            except:
                raise ValueError("请检查您的输入")

        data = xlwt.Workbook(encoding='utf-8')
        sheet = data.add_sheet('sheet1', cell_overwrite_ok=True)

        # 单元格格式
        alignment = xlwt.Alignment()  # Create Alignment
        # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        # May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
        alignment.vert = xlwt.Alignment.VERT_CENTER
        alignment.wrap = 1  # 自动换行
        style = xlwt.XFStyle()  # Create Style
        style.alignment = alignment  # Add Alignment to Style

        users = dict()
        users_map_name = dict()
        contest_name = []
        cnt = 1
        for it in contest:
            contest_name.append(it.title)
            if len(it.standings) < 5:
                raise ValueError("请检查是否有测试未生成静态数据")
            contest_problem = it.contestproblem_set.all()
            n = len(contest_problem)
            rank_list = eval(it.standings)
            for ele in rank_list:
                user = ele[0][0]
                if users.get(user) == None:
                    users[user] = []
                    users_map_name[user] = ele[0][1]
                dif = cnt - len(users[user]) - 1
                for j in range(dif):
                    users[user].append(0.0)
                users[user].append(round(ele[2] / n, 2))
            for it in users.items():
                if len(it[1]) < cnt:
                    it[1].append(0.0)
            cnt += 1
        sorted_users = sorted(users.keys())
        sheet.write(0, 0, "学号", style)
        sheet.write(0, 1, "姓名", style)
        col = 2
        for name in contest_name:
            sheet.write(0, col, name, style)
            col += 1
        sheet.write(0, col, "总成绩", style)
        raw = 1
        contest_count = len(contest)
        for user in sorted_users:
            sheet.write(raw, 0, user, style)
            sheet.write(raw, 1, users_map_name[user], style)
            col = 2
            sum = 0
            for score in users[user]:
                sheet.write(raw, col, score, style)
                sum += score
                col += 1
            sheet.write(raw, col, round(sum / contest_count, 2), style)
            raw += 1

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
                download_name = '实验成绩综合.xls'
                response = HttpResponse(f)
                response['content_type'] = "application/octet-stream"
                response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(
                    escape_uri_path(download_name))
                return response
            except Exception:
                raise Http404


class VisualizationView(View):
    template_name = 'contest/submission_peak.jinja2'

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        contest = Contest.objects.get(id=pk)
        if not request.user.is_superuser and contest.status != 1:
            return redirect(reverse('contest:list'))
        if len(contest.visualization) < 5:
            return redirect(reverse('contest:list'))
        data = eval(contest.visualization)
        return render(request, self.template_name, {'times': data[0],
                                                    'contest': contest,
                                                    'n1': data[2],
                                                    'length1': data[3],
                                                    'step1': data[4],
                                                    'start_time': contest.start_time,
                                                    'correct_submission': data[6],
                                                    'all_submission': data[7],
                                                    'average_score': data[8],
                                                    'correct_radio': data[9],
                                                    'problem_name': data[10],
                                                    'max_submission_times': data[11],
                                                    'all_pie_chart': data[12],
                                                    'code_length_data': data[13],
                                                    'scatter_chart_problem_id': data[14]
                                                    })
