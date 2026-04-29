"""
URL configuration for thesistrack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from dashboard import views as dashboard_views

urlpatterns = [
    path('admin/reports/', dashboard_views.admin_reports_home, name='admin-reports-home-root'),
    path('admin/reports/projects/', dashboard_views.report_project_progress, name='admin-report-project-progress-root'),
    path('admin/reports/projects/export/csv/', dashboard_views.export_project_progress_csv, name='admin-export-project-progress-root'),
    path('admin/reports/submissions/', dashboard_views.report_submission_approvals, name='admin-report-submissions-root'),
    path('admin/reports/submissions/export/csv/', dashboard_views.export_submissions_csv, name='admin-export-submissions-root'),
    path('admin/reports/supervisors/', dashboard_views.report_supervisor_performance, name='admin-report-supervisors-root'),
    path('admin/reports/supervisors/export/csv/', dashboard_views.export_supervisors_csv, name='admin-export-supervisors-root'),
    path('admin/reports/groups/', dashboard_views.report_group_performance, name='admin-report-groups-root'),
    path('admin/reports/groups/export/csv/', dashboard_views.export_groups_csv, name='admin-export-groups-root'),
    path('admin/reports/titles/', dashboard_views.report_title_approvals, name='admin-report-title-approvals-root'),
    path('admin/reports/titles/export/csv/', dashboard_views.export_title_approvals_csv, name='admin-export-title-approvals-root'),
    path('admin/reports/system-activity/', dashboard_views.report_system_activity, name='admin-report-system-activity-root'),
    path('admin/reports/system-activity/export/csv/', dashboard_views.export_system_activity_csv, name='admin-export-system-activity-root'),
    path('admin/reports/stalled/', dashboard_views.report_stalled_projects, name='admin-report-stalled-projects-root'),
    path('admin/reports/stalled/export/csv/', dashboard_views.export_stalled_projects_csv, name='admin-export-stalled-projects-root'),
    path('admin/reports/defense-stage/', dashboard_views.report_defense_stage, name='admin-report-defense-stage-root'),
    path('admin/reports/defense-stage/export/csv/', dashboard_views.export_defense_stage_csv, name='admin-export-defense-stage-root'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('dashboard.urls')),
    path('projects/', include('projects.urls')),
    path('attendance/', include('attendance.urls')),
    path('notifications/', include('notifications.urls')),
    path('core/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
