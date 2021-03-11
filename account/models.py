from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import BaseValidator


class UsernameValidator(UnicodeUsernameValidator):
    regex = r'^[\w.+-]+$'
    message = (
        '请输入正确的用户名，用户名只能包括字母、数字、下划线、.、+ 和 -。'
    )


class UsernameLengthValidator(BaseValidator):
    message = "用户名至少包含6个字符"
    code = 'min_length'

    def compare(self, a, b):
        return a < b

    def clean(self, x):
        try:
            return len(x.encode("GBK"))
        except UnicodeEncodeError:
            return len(x)


class User(AbstractUser):
    username_validators = [UsernameValidator(), UsernameLengthValidator(6)]
    username = models.CharField("用户名", max_length=30, unique=True,
                                validators=username_validators,
                                error_messages={
                                    'unique': "该用户名已存在"
                                })
    email = models.EmailField("邮箱", max_length=192, unique=True,
                              error_messages={
                                  'unique': "该邮箱已被注册"
                              })
    name = models.CharField("姓名", max_length=60, blank=True, null=True, default=None)
    school_class = models.ForeignKey('schoolclass.SchoolClass', on_delete=models.CASCADE, blank=True, null=True, default=None)
    is_student = models.BooleanField('学生', default=True)
    is_teacher = models.BooleanField('教师', default=False)
    polygon_enabled = models.BooleanField('是否允许参与管理', default=False)
    ac_total = models.PositiveIntegerField("累计做题数", default=0)
    submit_total = models.PositiveIntegerField("累计提交数", default=0)

    def __str__(self):
        return self.username
