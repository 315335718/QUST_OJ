import json
from datetime import datetime

from django.db import models
from django.db.models import Count
from django.utils import timezone

from account.models import User
from problem.models import Problem


class ContestManager(models.Manager):
    def get_status_list(self, show_all=False, filter_user=None, sorting_by_id=False, contest_type=None):
        q = models.Q()
        if not show_all:
            q &= models.Q(access_level__gt=0)
            if filter_user:
                q |= models.Q(managers=filter_user)
        if contest_type is not None:
            q &= models.Q(contest_type=contest_type)
        contest_list = self.get_queryset().prefetch_related('managers'). \
            annotate(Count('participants', distinct=True)).filter(q)

        if sorting_by_id:
            contest_list = contest_list.order_by("-pk").distinct()
        else:
            contest_list = contest_list.order_by("-start_time").distinct()
        return contest_list


class Contest(models.Model):
    ACCESS_LEVEL_OPTIONS = (
        (0,  '仅管理员可见'),
        (10, '受邀请'),
        (20, '公开'),
    )

    title = models.CharField("标题", max_length=192)
    description = models.TextField("描述", blank=True)
    contest_type = models.IntegerField('类型', default=0, choices=(
        (0, '测试'),
        (1, '作业'),
    ))
    start_time = models.DateTimeField("开始时间 (例:2020/08/06 9:38)", default=timezone.now)
    end_time = models.DateTimeField("结束时间 (例:2020/08/06 9:38)", default=timezone.now)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    is_best_counts = models.BooleanField("是否使用最高成绩", default=False)
    is_time_score = models.BooleanField("得分是否随时间衰减", default=False)
    time_score_wait = models.IntegerField('多长时间后分数衰减（分钟）', default=20)
    standings_to_student = models.BooleanField('是否排行榜展示给学生', default=True)
    max_try = models.IntegerField('最大尝试次数', default=3)
    invitation_code = models.CharField("邀请码(当比赛的访问控制为「受邀请时」使用)", max_length=192, default='123456')

    problems = models.ManyToManyField(Problem, through='ContestProblem')
    participants = models.ManyToManyField(User, through='ContestParticipant', related_name='contests')

    access_level = models.PositiveIntegerField("访问控制", default=0, choices=ACCESS_LEVEL_OPTIONS)

    objects = ContestManager()
    managers = models.ManyToManyField(User, related_name='managing_contests')

    class Meta:
        ordering = ['-pk']

    @property
    def status(self):
        now = timezone.now()
        if self.start_time is not None and now < self.start_time:
            return -1
        if self.end_time is not None and now > self.end_time:
            return 1
        return 0

    @property
    def finite(self):
        return self.start_time is not None and self.end_time is not None

    @property
    def length(self):
        if not self.finite:
            return None
        return self.end_time - self.start_time

    @property
    def contest_problem_list(self):
        if not hasattr(self, '_contest_problem_list'):
            self._contest_problem_list = list(self.contestproblem_set.select_related('problem').
                                            defer('problem__description', 'problem__cases').all())
        return self._contest_problem_list

    def get_contest_problem(self, problem_id):
        get_result = list(filter(lambda p: p.problem_id == problem_id, self.contest_problem_list))
        if len(get_result) > 0:
            return get_result[0]
        else:
            return None

    def add_contest_problem_to_submissions(self, submissions):
        find_contest_problem = {k.problem_id: k for k in self.contest_problem_list}
        for submission in submissions:
            submission.contest_problem = find_contest_problem.get(submission.problem_id)

    @property
    def participants_ids(self):
        if not hasattr(self, '_contest_user_ids'):
            self._contest_user_ids = list(self.contestparticipant_set.order_by().values_list("user_id", flat=True))
        return self._contest_user_ids

    def fetch_problem_entities_from_ids(self, problem_ids):
        pool = {t.problem_id: t for t in self.contest_problem_list}
        return [pool[problem_id] for problem_id in problem_ids]

    def __str__(self):
        return self.title


class ContestProblem(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=12)

    ac_user_count = models.PositiveIntegerField(default=0)
    total_user_count = models.PositiveIntegerField(default=0)
    ac_count = models.PositiveIntegerField(default=0)
    total_count = models.PositiveIntegerField(default=0)
    first_yes_time = models.DurationField(null=True, blank=True)
    first_yes_by = models.PositiveIntegerField(null=True, blank=True)
    max_score = models.FloatField(default=0)
    avg_score = models.FloatField(default=0)

    class Meta:
        unique_together = ('problem', 'contest')
        ordering = ['identifier']

    @property
    def user_ratio(self):
        return self.ac_user_count / self.total_user_count if self.total_user_count > 0 else 0.0

    @property
    def ratio(self):
        return self.ac_count / self.total_count if self.total_count > 0 else 0.0

    def __str__(self):
        return self.identifier + '. ' + self.problem.title

class ContestParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    detail_raw = models.TextField(blank=True)
    is_disabled = models.BooleanField(default=False)
    join_time = models.DateTimeField(blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)

    def start_time(self, contest: Contest):
        # the contest should be a cached contest
        if self.join_time is None:
            return contest.start_time
        else:
            return self.join_time

    def end_time(self, contest: Contest):
        st = self.start_time(contest)
        if st is None or contest.end_time is None:
            return contest.end_time
        return st + (contest.end_time - contest.start_time)

    def as_contest_time(self, contest: Contest, real_time):
        return real_time - self.start_time(contest)

    def status(self, contest: Contest):
        start_time = self.start_time(contest)
        end_time = self.end_time(contest)
        if start_time is not None and datetime.now() < start_time:
            return -1
        if end_time is not None and datetime.now() > end_time:
            return 1
        return 0

    @property
    def detail(self):
        try:
            if hasattr(self, "_detail"):
                return self._detail
            if not self.detail_raw:
                return {}
            self._detail = {int(k): v for k, v in json.loads(self.detail_raw).items()}
            return self._detail
        except:
            return {}

    @detail.setter
    def detail(self, d):
        self.detail_raw = json.dumps(d)

    class Meta:
        unique_together = ["user", "contest"]
        ordering = ("-is_confirmed", "-score")