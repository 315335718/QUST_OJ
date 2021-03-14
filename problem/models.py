import re

from django.db import models


from account.models import User

class Problem(models.Model):
    title = models.CharField("题目名称", max_length=192)
    description = models.TextField("题目描述")
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    checker = models.TextField("参考答案")
    table_to_delete = models.TextField("要删除的表", blank=True)
    table_to_do = models.TextField("要进行其他操作的表", blank=True)

    address = models.CharField("测试点地址", max_length=192, blank=True)
    case_total = models.IntegerField("测试点数", blank=True, default=0)
    cases = models.TextField("测试点", blank=True)
    points = models.TextField("测试点分数", blank=True)

    problem_type = models.CharField("题目类型", max_length=20, choices=(
        ('查询类', '查询类'),
        ('更新类', '更新类'),
        ('创建视图类', '创建视图类'),
        ('创建基本表', '创建基本表'),
    ), default='查询类')
    level = models.CharField("题目难度", max_length=20, choices=(
        ('简单', '简单'),
        ('中等', '中等'),
        ('较难', '较难'),
        ('困难', '困难'),
    ), default='中等')

    visible = models.BooleanField('是否可见', default=True)
    managers = models.ManyToManyField(User, related_name='managing_problems')

    ac_user_count = models.PositiveIntegerField(default=0)
    total_user_count = models.PositiveIntegerField(default=0)
    ac_count = models.PositiveIntegerField(default=0)
    total_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return '%d. %s' % (self.pk, self.title)

    class Meta:
        ordering = ["-pk"]
        verbose_name_plural = '题目'

    @property
    def case_list(self):
        return list(filter(lambda x: x, re.split(r"[,;]", self.cases)))

    @property
    def point_list(self):
        return list(
        map(int, list(filter(lambda x: x, self.points.split(',')))))  # point list should be as long as case list

    def _status_count(self, status):
        return self.submission_set.filter(status=status, visible=True).values("id").count()

    @property
    def ac_user_ratio(self):
        return self.ac_user_count / self.total_user_count if self.total_user_count > 0 else 0.0

    @property
    def ac_ratio(self):
        return self.ac_count / self.total_count if self.total_count > 0 else 0.0

    # @property
    # def stats(self):
    #     ret = {
    #     "ac": self.ac_count,
    #     "wa": self._status_count(SubmissionStatus.WRONG_ANSWER),
    #     "tle": self._status_count(SubmissionStatus.TIME_LIMIT_EXCEEDED),
    #     "re": self._status_count(SubmissionStatus.RUNTIME_ERROR),
    #     "ce": self._status_count(SubmissionStatus.COMPILE_ERROR)
    #     }
    #     ret["others"] = self.total_count - sum(ret.values())
    #     return ret

