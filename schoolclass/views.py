import time
import random
import pandas

from django.shortcuts import render, reverse
from django.views.generic import View, FormView
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password

from .forms import SchoolClassForm, AddStudentForm, UpdateClassForm, ExcelInputForm
from .models import SchoolClass
from account.models import User


class AddClassView(FormView):
    template_name = 'schoolclass/add_class.jinja2'
    form_class = SchoolClassForm

    def form_valid(self, form):
        if not self.request.user.is_authenticated or not self.request.user.is_superuser:
            return HttpResponseRedirect('/')
        teacher = self.request.user
        form.create(teacher.id)
        self.success_url = reverse('schoolclass:show_class', kwargs={'pk': 0})
        return super().form_valid(form)


class UpdateClassView(FormView):
    template_name = 'schoolclass/update_class.jinja2'
    form_class = UpdateClassForm

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.request.user.is_superuser:
            return HttpResponseRedirect('/')
        class_id = self.kwargs['pk']
        try:
            school_class = SchoolClass.objects.get(id=class_id)
        except:
            return HttpResponseRedirect('/reject/')
        if school_class.tercher_id != request.user.id:
            return HttpResponseRedirect('/reject/')
        form = self.form_class(instance=school_class)
        cur = {'form': form, 'class_id': class_id}
        return self.render_to_response(cur)

    def form_valid(self, form, class_id):
        form.create(form, class_id)
        self.success_url = reverse('schoolclass:show_class', kwargs={'pk': class_id})
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = UpdateClassForm(request.POST)
        if form.is_valid():
            class_id = self.kwargs['pk']
            return self.form_valid(form, class_id)
        else:
            return self.form_invalid(form)


class DeleteClassView(View):
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.request.user.is_superuser:
            return HttpResponseRedirect('/')
        class_id = kwargs.get('pk')
        try:
            school_class = SchoolClass.objects.get(id=class_id)
        except:
            return HttpResponseRedirect('/reject/')
        if school_class.tercher_id != request.user.id:
            return HttpResponseRedirect('/reject/')
        if User.objects.filter(school_class=school_class).exists():
            s_url = reverse('schoolclass:show_class', kwargs={'pk': class_id})
        else:
            SchoolClass.objects.filter(id=class_id).delete()
            s_url = reverse('schoolclass:show_class', kwargs={'pk': 0})
        return HttpResponseRedirect(s_url)


class AddStudentView(FormView):
    template_name = 'schoolclass/add_student.jinja2'
    form_class = AddStudentForm

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.request.user.is_superuser:
            return HttpResponseRedirect('/')
        class_id = self.kwargs['pk']
        try:
            school_class = SchoolClass.objects.get(id=class_id)
        except:
            return HttpResponseRedirect('/reject/')
        if school_class.tercher_id != request.user.id:
            return HttpResponseRedirect('/reject/')
        form = self.form_class()
        cur = {'form': form, 'class_id': class_id}
        return self.render_to_response(cur)

    def post(self, request, *args, **kwargs):
        form = AddStudentForm(request.POST)
        if form.is_valid():
            class_pk = self.kwargs.get('pk')
            return self.form_valid(form, class_pk)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, class_pk):
        form.create(class_pk)
        self.success_url = reverse('schoolclass:show_class', kwargs={'pk': class_pk})
        return super().form_valid(form)


class DeleteStudentView(View):
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.request.user.is_superuser:
            return HttpResponseRedirect('/')
        student_id = kwargs.get('s_pk')
        class_id = kwargs.get('c_pk')
        try:
            User.objects.filter(id=student_id).delete()
        except:
            HttpResponseRedirect('reject')
        s_url = reverse('schoolclass:show_class', kwargs={'pk': class_id})
        return HttpResponseRedirect(s_url)


class DeleteALLStudentView(View):
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.request.user.is_superuser:
            return HttpResponseRedirect('/')
        class_id = kwargs.get('pk')
        try:
            school_class = SchoolClass.objects.get(id=class_id)
        except:
            return HttpResponseRedirect('/reject/')
        if school_class.tercher_id != request.user.id:
            return HttpResponseRedirect('/reject/')
        User.objects.filter(school_class_id=class_id).delete()
        s_url = reverse('schoolclass:show_class', kwargs={'pk': class_id})
        return HttpResponseRedirect(s_url)


class ShowClassView(FormView):
    template_name = 'schoolclass/show_class.jinja2'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.request.user.is_superuser:
            return HttpResponseRedirect('/')
        cur_pk = kwargs.get('pk')
        teacher = self.request.user
        t_id = teacher.id
        school_class = SchoolClass.objects.filter(tercher_id=t_id)
        sc = ''
        if (cur_pk == '0' or cur_pk == 0) and len(school_class) > 0:
            sc = school_class[0]
        elif len(school_class) > 0:
            sc = SchoolClass.objects.get(id=cur_pk)
        student_list = []
        if sc != '':
            student_list = User.objects.filter(school_class_id=sc.id)
        else:
            sc = dict()
            sc['id'] = 0
        return render(request, self.template_name, {'class_list': school_class, 'student_list': student_list, 'cur_class': sc})


class ResetPasswordView(View):
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.request.user.is_superuser:
            return HttpResponseRedirect('/')
        student_id = kwargs.get('s_pk')
        class_id = kwargs.get('c_pk')
        try:
            user = User.objects.get(id=student_id)
            user.set_password('12345678')
            user.save()
        except:
            return HttpResponseRedirect('/reject/')
        s_url = reverse('schoolclass:show_class', kwargs={'pk': class_id})
        return HttpResponseRedirect(s_url)


class AddStudentsByExcelView(View):
    template_name = 'schoolclass/student_excel.jinja2'
    form_class = ExcelInputForm

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated or not self.request.user.is_superuser:
            return HttpResponseRedirect('/')
        form = self.form_class()
        pk = kwargs.get('pk')
        return render(request, self.template_name, {'form': form, 'schoolclass_id': pk})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            pk = kwargs.get('pk')
            # data = xlrd.open_workbook(filename=None, file_contents=self.request.FILES['excel'].read())
            # sheet = data.sheet_by_index(0)
            # n = sheet.nrows
            # username = str(sheet.cell_value(i, 0))
            df = pandas.read_excel(self.request.FILES['excel'].read())
            data = df.values.tolist()
            n = len(data)
            for i in range(n):
                username = str(data[i][0])
                name = str(data[i][1])
                password = make_password(str(data[i][2]))
                if User.objects.filter(username=username).exists():
                    User.objects.filter(username=username).update(name=name, password=password, school_class_id=pk)
                    # user.save(update_fields=['name', 'password', 'school_class_id'])
                else:
                    ticks = int(time.time())
                    fake_email = str(ticks) + str(random.randint(1, 100)) + str(random.randint(1, 100)) + '@' + 'qq.com'
                    User.objects.create(username=username, password=password, email=fake_email, name=name, school_class_id=pk)
        return HttpResponseRedirect(reverse('schoolclass:show_class', kwargs={'pk': pk}))