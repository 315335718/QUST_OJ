import json

from django.db import models

from problem.models import Problem
from account.models import User
from contest.models import Contest
from submission.utils import SubmissionStatus, STATUS_CHOICE


class Submission(models.Model):
    code = models.TextField(blank=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    judge_end_time = models.DateTimeField(blank=True, null=True)

    code_length = models.PositiveIntegerField(blank=True, null=True)
    judge_server = models.IntegerField(default=0)

    status = models.IntegerField(choices=STATUS_CHOICE, db_index=True, default=SubmissionStatus.SUBMITTED)
    status_percent = models.FloatField(default=0)
    status_detail = models.TextField(blank=True)
    status_message = models.TextField(blank=True)
    running_process = models.CharField(blank=True, max_length=192)

    contest = models.ForeignKey(Contest, on_delete=models.SET_NULL, null=True)
    contest_time = models.DurationField(null=True, blank=True)

    visible = models.BooleanField(default=True, db_index=True)
    ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return '%d. %s --- %s' % (self.pk, self.author.username, self.problem.title)

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ, signature-differs
        self.code_length = len(self.code.encode())
        return super(Submission, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-create_time']
        verbose_name_plural = '题目提交信息'

    @property
    def verbose_status(self):
        return dict(STATUS_CHOICE)[self.status]

    # @property
    # def create_time_display(self):
    #     return datetime_display(self.create_time)
    #
    # @property
    # def judge_time_display(self):
    #     return datetime_display(self.judge_end_time)

    # @property
    # def code_as_html(self):
    #     return transform_code_to_html(self.code, self.lang)

    @property
    def status_detail_list(self):
        try:
            return json.loads(self.status_detail)
        except json.JSONDecodeError:
            return []

    @status_detail_list.setter
    def status_detail_list(self, lis):
        self.status_detail = lis
        # self.status_detail = json.dumps(lis)

    @property
    def status_detail_display(self):
        r, l = [], self.status_detail_list
        status_dictionary = dict(STATUS_CHOICE)
        count = len(l)
        re_count, last_group = 1, 0
        for index, s in enumerate(l, start=1):
            u, v = -233, '%d/%d' % (index, count)  # Magic number: display nothing
            if 'verdict' in s:
                if 'group' in s:
                    if s['group'] != last_group:
                        re_count = 1
                    last_group = s['group']
                    u = s['verdict']
                    v = '%d-%d' % (s['group'], re_count)
                    re_count += 1
                if SubmissionStatus.is_judged(s['verdict']):
                    u = s['verdict']
                    t = status_dictionary[u]
                    if s['verdict'] in (SubmissionStatus.ACCEPTED, SubmissionStatus.SCORED,):
                        t += ', %.3fs' % s.get('time', 0.0)
                    elif s['verdict'] == SubmissionStatus.RUNTIME_ERROR:
                        t += ', %s' % s.get('message', 'NaN')
                    v += ': ' + t
                elif 'group' in s:
                    v += ": Skipped"
            if 'point' in s:
                v += ' (%.1f)' % s['point']
            r.append((u, v))
        return r

    @property
    def is_judged(self):
        return SubmissionStatus.is_judged(self.status)

    def get_time_display(self):
        if self.status_time is not None and self.status >= SubmissionStatus.WRONG_ANSWER and \
                self.status != SubmissionStatus.COMPILE_ERROR:
            return '%.3f' % self.status_time
        else:
            return 'N/A'

    def get_memory_display(self):
        if self.status_memory is not None and self.status >= SubmissionStatus.WRONG_ANSWER and \
                self.status != SubmissionStatus.COMPILE_ERROR:
            return '%.3f' % self.status_memory
        else:
            return 'N/A'

    @property
    def status_score(self):
        if hasattr(self, 'contest_problem'):
            return int(round(self.contest_problem.weight / 100 * self.status_percent + 1E-2))
        return int(round(self.status_percent))


class SubmissionReport(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
