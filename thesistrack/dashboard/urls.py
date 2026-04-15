from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('student/', views.student_dashboard, name='student-dashboard'),
    path('supervisor/', views.supervisor_dashboard, name='supervisor-dashboard'),
    path('adminstrator/', views.admin_dashboard, name='admin-dashboard'),
]