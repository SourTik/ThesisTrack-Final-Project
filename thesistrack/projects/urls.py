from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project-list'),
    path('submit/', views.submit_project, name='submit-project'),
    path('<int:project_id>/submit-doc/', views.submit_document, name='submit-document'),
    path('<int:project_id>/approve/', views.approve_project, name='approve-project'),
    path('submissions/<int:submission_id>/review/', views.review_submission, name='review-submission'),
]