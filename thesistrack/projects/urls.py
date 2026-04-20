from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project-list'),
    path('supervisor/dashboard/', views.supervisor_dashboard, name='supervisor-dashboard'),
    path('supervisor/projects/', views.supervisor_assigned_projects, name='supervisor-project-list'),
    path('supervisor/projects/<int:project_id>/', views.supervisor_project_detail, name='supervisor-project-detail'),
    path('groups/create/', views.create_group, name='create-group'),
    path('submit/', views.submit_project, name='submit-project'),
    path('<int:project_id>/submit-doc/', views.submit_document, name='submit-document'),
    path('<int:project_id>/approve/', views.approve_project, name='approve-project'),
    path('<int:project_id>/reject/', views.reject_project, name='reject-project'),
    path('<int:project_id>/assign-supervisor/', views.assign_supervisor, name='assign-supervisor'),
    path('submissions/<int:submission_id>/review/', views.review_submission, name='review-submission'),
]