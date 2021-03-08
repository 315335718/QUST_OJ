import os
import time
import random
import re
import datetime

from django import forms
from django.http import HttpResponseRedirect
from django.db import models

from problem.models import Problem
from polygon.analyse import get_table
from contest.models import Contest


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['title', 'description', 'checker', 'problem_type', 'level', 'visible']
        error_messages = {
            'title': {
                'require': "请输入题目名称。"
            },
            'description': {
                'require': "请输入题目描述"
            },
            'checker': {
                'require': "请输入正确代码"
            },
            'problem_type': {
                'require': "请选择题目类型"
            }
        }

    def create(self):
        instance = self.save(commit=False)
        new_id = 1
        if Problem.objects.exists():
            new_id = Problem.objects.order_by("id").last().id + 1
            instance.id = new_id
        else:
            instance.id = 1
        dirpath = str(os.path.abspath(os.path.join(os.getcwd())))
        dirpath += '/cases/' + str(new_id)
        os.makedirs(dirpath)
        instance.address = dirpath
        info = get_table(instance.problem_type, instance.description, instance.checker)
        instance.table_to_delete = info['table_to_delete']
        instance.table_to_do = info['other']
        instance.save()

    def clean(self):
        data = super(ProblemForm, self).clean()
        return data


class UpdateProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['title', 'description', 'checker', 'problem_type', 'level']
        error_messages = {
            'title': {
                'require': "请输入题目名称。"
            },
            'description': {
                'require': "请输入题目描述"
            },
            'checker': {
                'require': "请输入正确代码"
            },
            'problem_type': {
                'require': "请选择题目类型"
            }
        }

    def create(self, form, problem_id):
        p = Problem.objects.get(pk=problem_id)
        p.title = form.data['title']
        p.description = form.data['description']
        p.checker = form.data['checker']
        p.problem_type = form.data['problem_type']
        p.level = form.data['level']
        info = get_table(p.problem_type, p.description, p.checker)
        p.table_to_delete = info['table_to_delete']
        p.table_to_do = info['other']
        p.save()

    def clean(self):
        data = super(UpdateProblemForm, self).clean()
        return data


class CaseForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, label='sql代码')


class UpdateCasesForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, label='sql代码')

    def create(self, form, problem_id, case_id):
        p = Problem.objects.get(pk=problem_id)
        case_list = list(filter(lambda x: x, re.split(r"[,;\[\]' ]", p.cases)))
        if len(case_list) == 0 or int(case_id) > len(case_list):
            return HttpResponseRedirect('/reject/')
        filename = case_list[int(case_id) - 1]
        sqlcode = form.data['content']
        with open(filename, 'w', encoding='utf-8') as file_object:
            file_object.write(sqlcode)


class UpdateContestForm(forms.ModelForm):
    class Meta:
        model = Contest
        exclude = ['problems', 'participants', 'managers', 'create_time', 'standings_to_student']

    field_order = ['title', 'description', 'contest_type', 'start_time', 'end_time', 'access_level', 'max_try',\
                   'invitation_code', 'is_best_count', 'is_time_score']

    def __init__(self, *args, **kwargs):
        super(UpdateContestForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(UpdateContestForm, self).clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        delta = end_time - start_time
        if delta < datetime.timedelta(minutes=1):
            delta = datetime.timedelta(hours=1)
            cleaned_data['end_time'] = end_time + delta
        return cleaned_data
