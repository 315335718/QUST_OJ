from django.urls import path

from problem.views import ProblemView, ProblemSubmitView, ProblemSubmissionsView
from problem.views import ProblemListView, AllSubmissionsView

urlpatterns = [
    path('<int:pk>/', ProblemView.as_view(), name='detail'),
    path('<int:pk>/<int:c_pk>/submit/', ProblemSubmitView.as_view(), name='submit'),
    path('<int:pk>/submissions/', ProblemSubmissionsView.as_view(), name='submissions'),
    path('list/', ProblemListView.as_view(), name='list'),
    path('submissions/', AllSubmissionsView.as_view(), name='submissions'),
]