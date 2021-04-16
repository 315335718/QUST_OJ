from django.urls import path

from submission.views import GetAllSubmissionView, GetOneProblemSubmissionView

urlpatterns = [
    path('get_all_submission/', GetAllSubmissionView.as_view(), name='get_all_submission'),
    path('get_one_problem_submission/<int:u_id>/<int:p_id>/', GetOneProblemSubmissionView.as_view(), name='get_one_problem_submission'),
]