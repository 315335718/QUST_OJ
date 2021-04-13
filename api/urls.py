from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from api.views import TestView, ProblemView, SubmissionsView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('test/', TestView.as_view(), name='test'),
    path('problem/', ProblemView.as_view(), name='problem'),
    path('submissions/', SubmissionsView.as_view(), name='submissions'),
]
