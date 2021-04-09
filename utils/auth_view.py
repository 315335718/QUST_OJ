import functools

from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash,
)
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from django.utils.http import is_safe_url
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

def deprecate_current_app(func):
    """
    Handle deprecation of the current_app parameter of the views.
    """

    @functools.wraps(func)
    def inner(*args, **kwargs):
        if 'current_app' in kwargs:
            current_app = kwargs.pop('current_app')
            request = kwargs.get('request', None)
            if request and current_app is not None:
                request.current_app = current_app
        return func(*args, **kwargs)

    return inner

def _get_login_redirect_url(request, redirect_to):
  # Ensure the user-originating redirection URL is safe.
    if not is_safe_url(url=redirect_to, allowed_hosts=request.get_host()):
        return resolve_url(settings.LOGIN_REDIRECT_URL)
    return redirect_to

@deprecate_current_app
@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name,
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          extra_context=None, redirect_authenticated_user=False):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.GET.get(redirect_field_name, request.POST.get(redirect_field_name, '/'))
    error_flag = 0

    if redirect_authenticated_user and request.user.is_authenticated:
        redirect_to = _get_login_redirect_url(request, redirect_to)
        if redirect_to == request.path:
            raise ValueError(
                "Redirection loop for authenticated user detected. Check that "
                "your LOGIN_REDIRECT_URL doesn't point to a login page."
            )
        return HttpResponseRedirect(redirect_to)
    elif request.method == "POST":
        username = request.POST['username']
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            request.session.set_expiry(None if form.cleaned_data['remember_me'] else 0)
            return HttpResponseRedirect(_get_login_redirect_url(request, redirect_to))
        else:
            error_flag = 1
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
        'error_flag': error_flag,
        'not_has': 1,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@deprecate_current_app
@never_cache
def logout(request, next_page=None,
           template_name='registration/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           extra_context=None):

    auth_logout(request)

    if next_page is not None:
        next_page = resolve_url(next_page)
    elif settings.LOGOUT_REDIRECT_URL:
        next_page = resolve_url(settings.LOGOUT_REDIRECT_URL)

    if (redirect_field_name in request.POST or
        redirect_field_name in request.GET):
        next_page = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name))
        # # Security check -- don't allow redirection to a different host.
        # if not is_safe_url(url=next_page, host=request.get_host()):
        #     next_page = request.path

    if next_page:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page)

    current_site = get_current_site(request)
    context = {
        'site': current_site,
        'site_name': current_site.name,
        'title': 'Logged out'
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def reject(request):
    return render(request, 'reject.jinja2')