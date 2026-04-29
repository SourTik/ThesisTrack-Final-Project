import csv
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import (
    Avg,
    Case,
    Count,
    DateTimeField,
    DurationField,
    ExpressionWrapper,
    F,
    Max,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from core.decorators import role_required
from attendance.models import StudentAttendance
from notifications.models import Notification
from projects.models import Feedback, Group, Project, Submission


@login_required
def home(request):
    if request.user.role == User.SUPERVISOR:
        return redirect('dashboard:supervisor-dashboard')
    if request.user.role == User.ADMIN or request.user.is_superuser:
        return redirect('dashboard:admin-dashboard')
    if request.user.role == User.STUDENT:
        return redirect('dashboard:student-dashboard')
    raise PermissionDenied('Unknown role for this user.')


@role_required(User.STUDENT)
def student_dashboard(request):
    group = Group.objects.filter(members=request.user).prefetch_related('members').first()
    project = Project.objects.filter(group=group).select_related('supervisor').first() if group else None
    latest_submission = (
        Submission.objects.filter(project=project)
        .select_related('chapter')
        .order_by('-submitted_at')
        .first()
        if project
        else None
    )
    latest_feedback = (
        Feedback.objects.filter(submission=latest_submission)
        .select_related('supervisor')
        .order_by('-created_at')
        .first()
        if latest_submission
        else None
    )
    attendance_count = StudentAttendance.objects.filter(student=request.user, status='PRESENT').count()
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(
        request,
        'dashboard/student_dashboard.html',
        {
            'group': group,
            'project': project,
            'latest_submission': latest_submission,
            'latest_feedback': latest_feedback,
            'attendance_count': attendance_count,
            'unread_notifications': unread_notifications,
        },
    )


@role_required(User.SUPERVISOR)
def supervisor_dashboard(request):
    supervised_projects = Project.objects.filter(supervisor=request.user).select_related('group').count()
    pending_reviews = Submission.objects.filter(project__supervisor=request.user, status=Submission.PENDING).count()
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    recent_reviews = (
        Feedback.objects.filter(supervisor=request.user)
        .select_related('submission__project', 'submission__chapter')
        .order_by('-created_at')[:5]
    )

    status_filter = request.GET.get('status', '').upper()
    allowed_filters = {Submission.PENDING, Submission.APPROVED, Submission.REJECTED}
    decisions_queryset = Submission.objects.filter(project__supervisor=request.user)
    if status_filter in allowed_filters:
        decisions_queryset = decisions_queryset.filter(status=status_filter)
    else:
        status_filter = ''

    latest_feedback = Feedback.objects.filter(submission=OuterRef('pk')).order_by('-created_at')
    recent_submission_decisions = (
        decisions_queryset
        .select_related('project', 'chapter')
        .annotate(feedback_preview=Subquery(latest_feedback.values('comment')[:1]))
        .order_by('-reviewed_at', '-submitted_at')[:10]
    )

    return render(
        request,
        'dashboard/supervisor_dashboard.html',
        {
            'supervised_projects': supervised_projects,
            'pending_reviews': pending_reviews,
            'unread_notifications': unread_notifications,
            'recent_reviews': recent_reviews,
            'recent_submission_decisions': recent_submission_decisions,
            'status_filter': status_filter,
        },
    )


@role_required(User.ADMIN)
def admin_dashboard(request):
    stats = {
        'students': User.objects.filter(role=User.STUDENT).count(),
        'supervisors': User.objects.filter(role=User.SUPERVISOR).count(),
        'groups': Group.objects.count(),
        'projects': Project.objects.count(),
        'pending_titles': Project.objects.filter(title_approved=False).count(),
        'pending_reviews': Submission.objects.filter(status=Submission.PENDING).count(),
    }
    return render(request, 'dashboard/admin_dashboard.html', {'stats': stats})


def _report_nav_items():
    return [
        {'name': 'Overview', 'url_name': 'dashboard:admin-reports-home'},
        {'name': 'Project Progress', 'url_name': 'dashboard:admin-report-project-progress'},
        {'name': 'Submissions', 'url_name': 'dashboard:admin-report-submissions'},
        {'name': 'Supervisors', 'url_name': 'dashboard:admin-report-supervisors'},
        {'name': 'Groups', 'url_name': 'dashboard:admin-report-groups'},
        {'name': 'Title Approvals', 'url_name': 'dashboard:admin-report-title-approvals'},
        {'name': 'System Activity', 'url_name': 'dashboard:admin-report-system-activity'},
        {'name': 'Stalled Projects', 'url_name': 'dashboard:admin-report-stalled-projects'},
        {'name': 'Defense Stage', 'url_name': 'dashboard:admin-report-defense-stage'},
    ]


def _ensure_admin(request):
    if request.user.role != User.ADMIN:
        return HttpResponseForbidden('Forbidden')
    return None


def _format_datetime(value):
    if not value:
        return ''
    return timezone.localtime(value).strftime('%Y-%m-%d %H:%M')


def _format_duration(value):
    if not value:
        return ''
    total_seconds = int(value.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f'{hours}h {minutes}m'


def _display_user(user):
    if not user:
        return 'Not assigned'
    return user.get_full_name() or user.username


def _with_querystring(request, url_name):
    base_url = reverse(url_name)
    query = request.GET.urlencode()
    if query:
        return f'{base_url}?{query}'
    return base_url


def _project_progress_queryset():
    return (
        Project.objects
        .select_related('group', 'supervisor')
        .prefetch_related('group__members')
        .annotate(
            latest_approved_chapter=Subquery(
                Submission.objects.filter(project=OuterRef('pk'), status=Submission.APPROVED)
                .order_by('-submitted_at')
                .values('chapter__name')[:1]
            ),
            latest_submitted_chapter=Subquery(
                Submission.objects.filter(project=OuterRef('pk'))
                .order_by('-submitted_at')
                .values('chapter__name')[:1]
            ),
        )
        .order_by('-updated_at')
    )


def _submission_queryset(status_filter):
    normalized_status = status_filter.upper()
    submissions = Submission.objects.select_related('project', 'chapter', 'uploaded_by')
    if normalized_status in {Submission.PENDING, Submission.APPROVED, Submission.REJECTED}:
        submissions = submissions.filter(status=normalized_status)
    else:
        normalized_status = ''

    reuploads_subquery = (
        Submission.objects.filter(project=OuterRef('project'), chapter=OuterRef('chapter'))
        .values('project')
        .annotate(total_versions=Count('id'))
        .values('total_versions')[:1]
    )
    submissions = submissions.annotate(reupload_count=Subquery(reuploads_subquery)).order_by('-submitted_at')
    return submissions, normalized_status


def _supervisor_queryset(supervisor_id):
    review_duration = ExpressionWrapper(
        F('supervised_projects__submissions__reviewed_at') - F('supervised_projects__submissions__submitted_at'),
        output_field=DurationField(),
    )

    supervisors = (
        User.objects
        .filter(role=User.SUPERVISOR)
        .annotate(
            assigned_projects=Count('supervised_projects', distinct=True),
            total_reviewed=Count(
                'supervised_projects__submissions',
                filter=Q(supervised_projects__submissions__reviewed_at__isnull=False),
                distinct=True,
            ),
            approved_count=Count(
                'supervised_projects__submissions',
                filter=Q(supervised_projects__submissions__status=Submission.APPROVED),
                distinct=True,
            ),
            rejected_count=Count(
                'supervised_projects__submissions',
                filter=Q(supervised_projects__submissions__status=Submission.REJECTED),
                distinct=True,
            ),
            avg_review_time=Avg(
                review_duration,
                filter=Q(supervised_projects__submissions__reviewed_at__isnull=False),
            ),
        )
        .order_by('username')
    )

    if supervisor_id.isdigit():
        supervisors = supervisors.filter(id=int(supervisor_id))
    return supervisors


def _group_queryset():
    return (
        Group.objects
        .select_related('project')
        .prefetch_related('members', 'project__submissions__chapter')
        .annotate(
            submissions_count=Count('project__submissions', distinct=True),
            approved_chapters=Count(
                'project__submissions__chapter',
                filter=Q(project__submissions__status=Submission.APPROVED),
                distinct=True,
            ),
            rejected_submissions=Count(
                'project__submissions',
                filter=Q(project__submissions__status=Submission.REJECTED),
                distinct=True,
            ),
        )
        .order_by('name')
    )


def _title_approval_queryset(state_filter):
    normalized_state = state_filter.lower()
    projects = (
        Project.objects
        .select_related('group', 'supervisor')
        .annotate(
            approval_date=Case(
                When(title_approved=True, then=F('updated_at')),
                default=Value(None),
                output_field=DateTimeField(),
            )
        )
        .order_by('-updated_at')
    )
    if normalized_state == 'approved':
        projects = projects.filter(title_approved=True)
    elif normalized_state == 'pending':
        projects = projects.filter(title_approved=False).exclude(status=Project.TITLE_REJECTED)
    elif normalized_state == 'rejected':
        projects = projects.filter(status=Project.TITLE_REJECTED)
    else:
        normalized_state = ''
    return projects, normalized_state


def _stalled_projects_queryset(days):
    normalized_days = int(days) if days.isdigit() and int(days) > 0 else 14
    cutoff = timezone.now() - timedelta(days=normalized_days)
    projects = (
        Project.objects
        .select_related('group', 'supervisor')
        .annotate(
            latest_submission_at=Max('submissions__submitted_at'),
            pending_submissions=Count(
                'submissions',
                filter=Q(submissions__status=Submission.PENDING),
                distinct=True,
            ),
        )
        .filter(
            Q(supervisor__isnull=True)
            | Q(pending_submissions__gt=0)
            | (
                Q(updated_at__lt=cutoff)
                & (Q(latest_submission_at__isnull=True) | Q(latest_submission_at__lt=cutoff))
            )
        )
        .order_by('updated_at')
    )
    return projects, normalized_days


def _defense_stage_querysets():
    completed_projects = (
        Project.objects.filter(status=Project.COMPLETED)
        .select_related('group', 'supervisor')
        .order_by('-updated_at')
    )
    ready_for_defense = (
        Project.objects
        .select_related('group', 'supervisor')
        .annotate(
            approved_submissions=Count(
                'submissions',
                filter=Q(submissions__status=Submission.APPROVED),
                distinct=True,
            ),
            pending_submissions=Count(
                'submissions',
                filter=Q(submissions__status=Submission.PENDING),
                distinct=True,
            ),
            rejected_submissions=Count(
                'submissions',
                filter=Q(submissions__status=Submission.REJECTED),
                distinct=True,
            ),
        )
        .filter(
            title_approved=True,
            supervisor__isnull=False,
            approved_submissions__gt=0,
            pending_submissions=0,
            rejected_submissions=0,
        )
        .exclude(status=Project.COMPLETED)
        .order_by('-updated_at')
    )
    return ready_for_defense, completed_projects


@role_required(User.ADMIN)
def admin_reports_home(request):
    context = {
        'report_nav_items': _report_nav_items(),
        'total_projects': Project.objects.count(),
        'total_submissions': Submission.objects.count(),
        'total_supervisors': User.objects.filter(role=User.SUPERVISOR).count(),
        'pending_titles': Project.objects.filter(title_approved=False).count(),
        'pending_reviews': Submission.objects.filter(status=Submission.PENDING).count(),
    }
    context['active_report'] = 'Overview'
    return render(request, 'dashboard/reports/reports_home.html', context)


@role_required(User.ADMIN)
def report_project_progress(request):
    projects = _project_progress_queryset()

    return render(
        request,
        'dashboard/reports/project_progress_report.html',
        {
            'projects': projects,
            'report_nav_items': _report_nav_items(),
            'active_report': 'Project Progress',
            'export_url': reverse('dashboard:admin-export-project-progress-csv'),
        },
    )


@role_required(User.ADMIN)
def report_submission_approvals(request):
    submissions, status_filter = _submission_queryset(request.GET.get('status', ''))

    return render(
        request,
        'dashboard/reports/submission_approval_report.html',
        {
            'submissions': submissions,
            'status_filter': status_filter,
            'report_nav_items': _report_nav_items(),
            'active_report': 'Submissions',
            'export_url': _with_querystring(request, 'dashboard:admin-export-submissions-csv'),
        },
    )


@role_required(User.ADMIN)
def report_supervisor_performance(request):
    supervisor_id = request.GET.get('supervisor', '').strip()
    supervisors = _supervisor_queryset(supervisor_id)

    return render(
        request,
        'dashboard/reports/supervisor_performance_report.html',
        {
            'supervisors': supervisors,
            'all_supervisors': User.objects.filter(role=User.SUPERVISOR).order_by('username'),
            'selected_supervisor': supervisor_id,
            'report_nav_items': _report_nav_items(),
            'active_report': 'Supervisors',
            'export_url': _with_querystring(request, 'dashboard:admin-export-supervisors-csv'),
        },
    )


@role_required(User.ADMIN)
def report_group_performance(request):
    groups = _group_queryset()

    return render(
        request,
        'dashboard/reports/group_performance_report.html',
        {
            'groups': groups,
            'report_nav_items': _report_nav_items(),
            'active_report': 'Groups',
            'export_url': reverse('dashboard:admin-export-groups-csv'),
        },
    )


@role_required(User.ADMIN)
def report_title_approvals(request):
    projects, state_filter = _title_approval_queryset(request.GET.get('state', ''))

    summary = {
        'approved': Project.objects.filter(title_approved=True).count(),
        'pending': Project.objects.filter(title_approved=False).exclude(status=Project.TITLE_REJECTED).count(),
        'rejected': Project.objects.filter(status=Project.TITLE_REJECTED).count(),
    }

    return render(
        request,
        'dashboard/reports/title_approval_report.html',
        {
            'projects': projects,
            'state_filter': state_filter,
            'summary': summary,
            'report_nav_items': _report_nav_items(),
            'active_report': 'Title Approvals',
            'export_url': _with_querystring(request, 'dashboard:admin-export-title-approvals-csv'),
        },
    )


@role_required(User.ADMIN)
def report_system_activity(request):
    summary = {
        'total_projects': Project.objects.count(),
        'total_submissions': Submission.objects.count(),
        'total_approvals': Submission.objects.filter(status=Submission.APPROVED).count(),
        'total_rejections': Submission.objects.filter(status=Submission.REJECTED).count(),
        'total_active_users': User.objects.filter(is_active=True).count(),
    }

    return render(
        request,
        'dashboard/reports/system_activity_report.html',
        {
            'summary': summary,
            'report_nav_items': _report_nav_items(),
            'active_report': 'System Activity',
            'export_url': reverse('dashboard:admin-export-system-activity-csv'),
        },
    )


@role_required(User.ADMIN)
def report_stalled_projects(request):
    projects, days = _stalled_projects_queryset(request.GET.get('days', '14').strip())

    return render(
        request,
        'dashboard/reports/stalled_projects_report.html',
        {
            'projects': projects,
            'days': days,
            'report_nav_items': _report_nav_items(),
            'active_report': 'Stalled Projects',
            'export_url': _with_querystring(request, 'dashboard:admin-export-stalled-projects-csv'),
        },
    )


@role_required(User.ADMIN)
def report_defense_stage(request):
    ready_for_defense, completed_projects = _defense_stage_querysets()

    return render(
        request,
        'dashboard/reports/defense_stage_report.html',
        {
            'completed_projects': completed_projects,
            'ready_for_defense': ready_for_defense,
            'report_nav_items': _report_nav_items(),
            'active_report': 'Defense Stage',
            'export_url': reverse('dashboard:admin-export-defense-stage-csv'),
        },
    )


@role_required(User.ADMIN)
def export_project_progress_csv(request):
    forbidden = _ensure_admin(request)
    if forbidden:
        return forbidden

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="project_progress_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Project Title', 'Group', 'Supervisor', 'Status', 'Current Chapter', 'Last Updated'])

    for project in _project_progress_queryset():
        writer.writerow([
            project.title,
            project.group.name if project.group else 'Unassigned',
            _display_user(project.supervisor),
            project.get_status_display(),
            project.latest_approved_chapter or project.latest_submitted_chapter or 'No submissions yet',
            _format_datetime(project.updated_at),
        ])
    return response


@role_required(User.ADMIN)
def export_submissions_csv(request):
    forbidden = _ensure_admin(request)
    if forbidden:
        return forbidden

    submissions, _ = _submission_queryset(request.GET.get('status', ''))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="submission_approval_report.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Project Title',
        'Group',
        'Supervisor',
        'Chapter',
        'Version',
        'Status',
        'Re-uploads',
        'Submitted At',
        'Reviewed At',
    ])

    for submission in submissions:
        project = submission.project
        writer.writerow([
            project.title,
            project.group.name if project.group else 'Unassigned',
            _display_user(project.supervisor),
            submission.chapter.name if submission.chapter else '-',
            submission.version,
            submission.get_status_display(),
            submission.reupload_count or 1,
            _format_datetime(submission.submitted_at),
            _format_datetime(submission.reviewed_at),
        ])
    return response


@role_required(User.ADMIN)
def export_supervisors_csv(request):
    forbidden = _ensure_admin(request)
    if forbidden:
        return forbidden

    supervisors = _supervisor_queryset(request.GET.get('supervisor', '').strip())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="supervisor_performance_report.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Supervisor',
        'Assigned Projects',
        'Reviewed Submissions',
        'Approved',
        'Rejected',
        'Average Review Time',
    ])

    for supervisor in supervisors:
        writer.writerow([
            supervisor.get_full_name() or supervisor.username,
            supervisor.assigned_projects,
            supervisor.total_reviewed,
            supervisor.approved_count,
            supervisor.rejected_count,
            _format_duration(supervisor.avg_review_time),
        ])
    return response


@role_required(User.ADMIN)
def export_groups_csv(request):
    forbidden = _ensure_admin(request)
    if forbidden:
        return forbidden

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="group_performance_report.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Group',
        'Project Title',
        'Supervisor',
        'Project Status',
        'Member Count',
        'Submissions',
        'Approved Chapters',
        'Rejected Submissions',
    ])

    for group in _group_queryset():
        project = group.project
        writer.writerow([
            group.name,
            project.title if project else 'No project',
            _display_user(project.supervisor) if project else 'Not assigned',
            project.get_status_display() if project else '-',
            group.members.count(),
            group.submissions_count,
            group.approved_chapters,
            group.rejected_submissions,
        ])
    return response


@role_required(User.ADMIN)
def export_title_approvals_csv(request):
    forbidden = _ensure_admin(request)
    if forbidden:
        return forbidden

    projects, _ = _title_approval_queryset(request.GET.get('state', ''))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="title_approval_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Project Title', 'Group', 'Supervisor', 'Title Status', 'Approval Date', 'Last Updated'])

    for project in projects:
        if project.status == Project.TITLE_REJECTED:
            title_status = 'Rejected'
        elif project.title_approved:
            title_status = 'Approved'
        else:
            title_status = 'Pending'

        writer.writerow([
            project.title,
            project.group.name if project.group else 'Unassigned',
            _display_user(project.supervisor),
            title_status,
            _format_datetime(project.approval_date),
            _format_datetime(project.updated_at),
        ])
    return response


@role_required(User.ADMIN)
def export_system_activity_csv(request):
    forbidden = _ensure_admin(request)
    if forbidden:
        return forbidden

    summary = {
        'Total Projects': Project.objects.count(),
        'Total Submissions': Submission.objects.count(),
        'Total Approvals': Submission.objects.filter(status=Submission.APPROVED).count(),
        'Total Rejections': Submission.objects.filter(status=Submission.REJECTED).count(),
        'Total Active Users': User.objects.filter(is_active=True).count(),
    }
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="system_activity_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Metric', 'Value'])
    for metric, value in summary.items():
        writer.writerow([metric, value])
    return response


@role_required(User.ADMIN)
def export_stalled_projects_csv(request):
    forbidden = _ensure_admin(request)
    if forbidden:
        return forbidden

    projects, days = _stalled_projects_queryset(request.GET.get('days', '14').strip())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="stalled_projects_{days}d_report.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Project Title',
        'Group',
        'Supervisor',
        'Status',
        'Pending Reviews',
        'Last Submission',
        'Last Updated',
    ])

    for project in projects:
        writer.writerow([
            project.title,
            project.group.name if project.group else 'Unassigned',
            _display_user(project.supervisor),
            project.get_status_display(),
            project.pending_submissions,
            _format_datetime(project.latest_submission_at),
            _format_datetime(project.updated_at),
        ])
    return response


@role_required(User.ADMIN)
def export_defense_stage_csv(request):
    forbidden = _ensure_admin(request)
    if forbidden:
        return forbidden

    ready_for_defense, completed_projects = _defense_stage_querysets()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="defense_stage_report.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Project Title',
        'Group',
        'Supervisor',
        'Status',
        'Section',
        'Last Updated',
    ])

    for project in ready_for_defense:
        writer.writerow([
            project.title,
            project.group.name if project.group else 'Unassigned',
            _display_user(project.supervisor),
            project.get_status_display(),
            'Ready for Defense',
            _format_datetime(project.updated_at),
        ])
    for project in completed_projects:
        writer.writerow([
            project.title,
            project.group.name if project.group else 'Unassigned',
            _display_user(project.supervisor),
            project.get_status_display(),
            'Completed',
            _format_datetime(project.updated_at),
        ])
    return response
