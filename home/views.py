from django.shortcuts import render, redirect, reverse


def home_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('problem:list'))
    else:
        return render(request, 'home/home.jinja2')


def forbidden_view(request, exception):
    return render(request, 'error/403.jinja2')