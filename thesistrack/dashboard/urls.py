from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('student/', views.student_dashboard, name='student-dashboard'),
    path('supervisor/', views.supervisor_dashboard, name='supervisor-dashboard'),
    path('administrator/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/reports/', views.admin_reports_home, name='admin-reports-home'),
    path('admin/reports/projects/', views.report_project_progress, name='admin-report-project-progress'),
    path('admin/reports/projects/export/csv/', views.export_project_progress_csv, name='admin-export-project-progress-csv'),
    path('admin/reports/submissions/', views.report_submission_approvals, name='admin-report-submissions'),
    path('admin/reports/submissions/export/csv/', views.export_submissions_csv, name='admin-export-submissions-csv'),
    path('admin/reports/supervisors/', views.report_supervisor_performance, name='admin-report-supervisors'),
    path('admin/reports/supervisors/export/csv/', views.export_supervisors_csv, name='admin-export-supervisors-csv'),
    path('admin/reports/groups/', views.report_group_performance, name='admin-report-groups'),
    path('admin/reports/groups/export/csv/', views.export_groups_csv, name='admin-export-groups-csv'),
    path('admin/reports/titles/', views.report_title_approvals, name='admin-report-title-approvals'),
    path('admin/reports/titles/export/csv/', views.export_title_approvals_csv, name='admin-export-title-approvals-csv'),
    path('admin/reports/system-activity/', views.report_system_activity, name='admin-report-system-activity'),
    path('admin/reports/system-activity/export/csv/', views.export_system_activity_csv, name='admin-export-system-activity-csv'),
    path('admin/reports/stalled/', views.report_stalled_projects, name='admin-report-stalled-projects'),
    path('admin/reports/stalled/export/csv/', views.export_stalled_projects_csv, name='admin-export-stalled-projects-csv'),
    path('admin/reports/defense-stage/', views.report_defense_stage, name='admin-report-defense-stage'),
    path('admin/reports/defense-stage/export/csv/', views.export_defense_stage_csv, name='admin-export-defense-stage-csv'),
]