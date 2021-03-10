from django.shortcuts import render, redirect, reverse


def home_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('problem:list'))
    else:
        return render(request, 'home/home.jinja2')
