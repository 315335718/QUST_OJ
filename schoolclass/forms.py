import time, random

from django import forms

from .models import SchoolClass
from account.models import User


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name', 'year', 'semester']
        error_messages = {
            'name': {
                'require': "请输入班级名。",
                'unique': "该班级已存在"
            },
        }

    def create(self, t_id):
        instance = self.save(commit=False)
        instance.tercher = User.objects.get(id=t_id)
        instance.save()

    def clean(self):
        data = super(SchoolClassForm, self).clean()
        return data


class UpdateClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name', 'year', 'semester']
        error_messages = {
            'name': {
                'require': "请输入班级名。",
                'unique': "该班级已存在"
            },
        }

    def create(self, form, class_id):
        sc = SchoolClass.objects.get(pk=class_id)
        sc.name = form.data['name']
        sc.year = form.data['year']
        sc.semester = form.data['semester']
        sc.save()

    def clean(self):
        data = super(UpdateClassForm, self).clean()
        return data


class AddStudentForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'name']
        error_messages = {
            'username': {
                'require': "请输入该学生学号。",
                'unique': "存在重复的学号"
            },
            'name': {
                'require': "请输入该学生姓名。"
            }
        }

    password = forms.CharField(help_text="至少六位",
                               widget=forms.PasswordInput,
                               min_length=6,
                               required=True,
                               error_messages={
                                   'min_length': "密码太短",
                                   'require': "请输入密码。"
                               }, )

    def create(self, class_pk):
        instance = self.save(commit=False)
        if User.objects.exists():
            new_id = User.objects.order_by("id").last().id + 1
            instance.id = new_id
        else:
            instance.id = 1
        ticks = int(time.time())
        fake_email = str(ticks) + str(random.randint(1, 100)) + str(random.randint(1, 100)) + '@' + 'qq.com'
        instance.email = fake_email
        instance.school_class = SchoolClass.objects.get(id=class_pk)
        instance.set_password(self.cleaned_data.get('password'))
        instance.save()
        return instance

    def clean(self):
        data = super(AddStudentForm, self).clean()
        return data
