from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from api.views import TestView, WxLoginView, SubmissionsView, TestView2
import api.problem.views as problem

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('test/', TestView.as_view(), name='test'),
    path('submissions/', SubmissionsView.as_view(), name='submissions'),
    path('test2/', TestView2.as_view(), name='test2'),
    path('problem_list/', problem.ProblemListView.as_view(), name='problem_list'),
    path('problem/', problem.ProblemView.as_view(), name='problem'),
    path('problem_submit/', problem.ProblemSubmitView.as_view(), name='problem_submit'),
    path('wx_login/', WxLoginView.as_view(), name='wx_login'),
]
