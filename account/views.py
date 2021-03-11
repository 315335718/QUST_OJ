from django.views.generic.edit import FormView
from django.shortcuts import HttpResponseRedirect, reverse
from django.contrib.auth import login

from account.forms import RegisterForm, LoginForm, ModifyPasswordForm
from utils import auth_view


class RegisterView(FormView):
    template_name = 'account/register.jinja2'
    form_class = RegisterForm
    success_url = '/'

    def form_valid(self, form):
        user = form.create()
        login(self.request, user)
        return super().form_valid(form)


def my_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('problem:list'))
    return auth_view.login(request, template_name='account/login.jinja2', authentication_form=LoginForm)


class ModifyPasswordView(FormView):
    template_name = 'account/password.jinja2'
    form_class = ModifyPasswordForm
    success_url = '/'

    def form_valid(self, form):
        return super().form_valid(form)