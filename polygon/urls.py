from django.urls import path

from polygon.views import ProblemListView, AddProblemView, UpdateProblemView, DeleteProblemView
from polygon.views import AddCaseView, UpdateCasesView, DeleteCaseView
from polygon.views import AddContestView, UpdateContestView, ContestListView, ContestProblemView, \
    ContestAddProblemView, ContestRemoveProblemView, ContestParticipantView, ContestAddOneParticipantView, \
    ContestAddParticipantByClassView, ContestRemoveUserView


urlpatterns = [
    path('problem/add_problem/', AddProblemView.as_view(), name='add_problem'),
    path('problem/list/', ProblemListView.as_view(), name='problem_list'),
    path('problem/<int:pk>/update_problem/', UpdateProblemView.as_view(), name='update_problem'),
    path('problem/<int:pk>/add_case/', AddCaseView.as_view(), name='add_case'),
    path('problem/<int:pk>/update_cases/<int:case_id>/', UpdateCasesView.as_view(), name='update_cases'),
    path('problem/<int:pk>/delete_cases/<int:case_id>/', DeleteCaseView.as_view(), name='delete_case'),
    path('problem/<int:pk>/delete_problem/', DeleteProblemView.as_view(), name='delete_problem'),

    path('contest/add_contest/', AddContestView.as_view(), name='add_contest'),
    path('contest/<int:pk>/update_contest/', UpdateContestView.as_view(), name='update_contest'),
    path('contest/list/', ContestListView.as_view(), name='contest_list'),
    path('contest/<int:pk>/problem/', ContestProblemView.as_view(), name='contest_problem'),
    path('contest/<int:pk>/add_problem/', ContestAddProblemView.as_view(), name='contest_add_problem'),
    path('contest/<int:pk>/remove_problem/<int:p_pk>/', ContestRemoveProblemView.as_view(), name='contest_remove_problem'),
    path('contest/<int:pk>/participant/', ContestParticipantView.as_view(), name='contest_participant'),
    path('contest/<int:pk>/add_one_participant/', ContestAddOneParticipantView.as_view(), name='contest_add_one_participant'),
    path('contest/<int:pk>/add_participant_by_class/', ContestAddParticipantByClassView.as_view(), name='add_participant_by_class'),
    path('contest/<int:pk>/remove_user/<int:u_pk>/', ContestRemoveUserView.as_view(), name='contest_remove_user'),
]
