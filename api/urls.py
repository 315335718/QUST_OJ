from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from api.views import TestView, WxLoginView, SubmissionsView, TestView2
import api.problem.views as problem
import api.submission.views as submission
import api.comment.views as comment
import api.contest.views as contest

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('test/', TestView.as_view(), name='test'),
    path('submissions/', SubmissionsView.as_view(), name='submissions'),
    path('test2/', TestView2.as_view(), name='test2'),
    path('wx_login/', WxLoginView.as_view(), name='wx_login'),

    # 题目
    path('problem_list/', problem.ProblemListView.as_view(), name='problem_list'),
    path('problem/', problem.ProblemView.as_view(), name='problem'),
    path('problem_submit/', problem.ProblemSubmitView.as_view(), name='problem_submit'),
    # 测试
    path('contest_list/', contest.ContestListView.as_view(), name='contest_list'),
    path('contest_dashboard/', contest.ContestDashboardView.as_view(), name='contest_dashboard'),
    path('contest_rank/', contest.ContestRankListView.as_view(), name='contest_rank'),
    # 提交信息
    path('my_submissions/', submission.MySubmissionsView.as_view(), name='my_submissions'),
    # 讨论区
    path('artical_creat/', comment.creat_articalView.as_view(), name='creat_articalView'),
    path('artical_list/', comment.list_articalView.as_view(), name='list_articalView'),
]