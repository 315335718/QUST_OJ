from django.urls import path

from contest.views import ContestListView, DashboardView, InvitationCodeInputView, ContestProblemView, \
    ContestMySubmissionsView, ContestSubmissionsView, StandingsView, OutputStandingsToExcelView, \
    VisualizationView, CreateStandingsAndVisualizationView, OutputMergedStandingsToExcelView

urlpatterns = [
    path('list/', ContestListView.as_view(), name='list'),
    path('<int:pk>/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('<int:pk>/invitation_code/', InvitationCodeInputView.as_view(), name='invitation_code'),
    path('<int:pk>/problem/<int:p_pk>/', ContestProblemView.as_view(), name='contest_problem'),
    path('<int:pk>/my_submissions/', ContestMySubmissionsView.as_view(), name='my_submissions'),
    path('<int:pk>/submissions/', ContestSubmissionsView.as_view(), name='submissions'),
    path('<int:pk>/create_data/', CreateStandingsAndVisualizationView.as_view(), name='create_data'),
    path('<int:pk>/standings/', StandingsView.as_view(), name='standings'),
    path('<int:pk>/standings_to_excel/', OutputStandingsToExcelView.as_view(), name='standings_to_excel'),
    path('merged_standings_to_excel/', OutputMergedStandingsToExcelView.as_view(), name='merged_standings_to_excel'),
    path('<int:pk>/visualization/', VisualizationView.as_view(), name='visualization'),
]