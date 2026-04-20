from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list, name='attendance-list'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_attendance_dashboard, name='admin_attendance_dashboard'),
    path('admin/mark/', views.admin_mark_attendance, name='admin_mark_attendance'),

    # Supervisor URLs
    path('supervisor/dashboard/', views.supervisor_attendance_dashboard, name='supervisor_attendance_dashboard'),
    path('supervisor/mark/', views.supervisor_mark_attendance, name='supervisor_mark_attendance'),

    # Student URLs
    path('student/dashboard/', views.student_attendance_dashboard, name='student_attendance_dashboard'),
]
