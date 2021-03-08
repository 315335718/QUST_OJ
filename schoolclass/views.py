from django.shortcuts import render, reverse
from django.views.generic import View, FormView
from django.http import HttpResponseRedirect

from .forms import SchoolClassForm, AddStudentForm, UpdateClassForm
from .models import SchoolClass
from account.models import User


class AddClassView(FormView):
    template_name = 'schoolclass/add_class.jinja2'
    form_class = SchoolClassForm

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            return HttpResponseRedirect('/reject/')
        teacher = self.request.user
        form.create(teacher.id)
        self.success_url = reverse('schoolclass:show_class', kwargs={'pk': 0})
        return super().form_valid(form)


class UpdateClassView(FormView):
    template_name = 'schoolclass/update_class.jinja2'
    form_class = UpdateClassForm

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return HttpResponseRedirect('/reject/')
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
        if not self.request.user.is_superuser:
            return HttpResponseRedirect('/reject/')
        class_id = kwargs.get('pk')
        try:
            school_class = SchoolClass.objects.get(id=class_id)
        except:
            return HttpResponseRedirect('/reject/')
        if school_class.tercher_id != request.user.id:
            return HttpResponseRedirect('/reject/')
        SchoolClass.objects.filter(id=class_id).delete()
        s_url = reverse('schoolclass:show_class', kwargs={'pk': 0})
        return HttpResponseRedirect(s_url)


class AddStudentView(FormView):
    template_name = 'schoolclass/add_student.jinja2'
    form_class = AddStudentForm

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return HttpResponseRedirect('/reject/')
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
        if not self.request.user.is_superuser:
            return HttpResponseRedirect('/reject/')
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
        if not self.request.user.is_superuser:
            return HttpResponseRedirect('/reject/')
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
        if not self.request.user.is_superuser:
            return HttpResponseRedirect('/reject/')
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
        return render(request, self.template_name,
                      {'class_list': school_class, 'student_list': student_list, 'cur_class': sc})


class ResetPasswordView(View):
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return HttpResponseRedirect('/reject/')
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
