from django.urls import path

from schoolclass.views import AddClassView, UpdateClassView, DeleteClassView, AddStudentView, DeleteStudentView, DeleteALLStudentView, ShowClassView, ResetPasswordView

urlpatterns = [
    path('add_class/', AddClassView.as_view(), name='add_class'),
    path('<int:pk>/update_class/', UpdateClassView.as_view(), name='update_class'),
    path('<int:pk>/delete_class/', DeleteClassView.as_view(), name='delete_class'),
    path('<int:pk>/add_student/', AddStudentView.as_view(), name='add_student'),
    path('<int:c_pk>/delete_student/<int:s_pk>/', DeleteStudentView.as_view(), name='delete_student'),
    path('<int:pk>/delete_all_student/', DeleteALLStudentView.as_view(), name='delete_all_student'),
    path('<int:pk>/show_class/', ShowClassView.as_view(), name='show_class'),
    path('<int:c_pk>/reset_password/<int:s_pk>/', ResetPasswordView.as_view(), name='reset_password'),
]