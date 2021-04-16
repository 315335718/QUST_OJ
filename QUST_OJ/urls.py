"""QUST_OJ URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from home.views import home_view, forbidden_view
from account.views import RegisterView, my_login, ModifyPasswordView
from utils.auth_view import logout, reject

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', my_login, name='login'),
    path('logout/', logout, name='logout'),
    path('password/', ModifyPasswordView.as_view(), name='password'),
    path('reject/', reject, name='reject'),
    path('polygon/', include(('polygon.urls', 'polygon'), namespace='polygon')),
    path('schoolclass/', include(('schoolclass.urls', 'schoolclass'), namespace='schoolclass')),
    path('problem/', include(('problem.urls', 'problem'), namespace='problem')),
    path('contest/', include(('contest.urls', 'contest'), namespace='contest')),
    path('api/', include(('api.urls', 'api'), namespace='api')),
    path('submission/', include(('submission.urls', 'submission'), namespace='submission')),
]

handler403 = forbidden_view
