from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import OuterRef, Subquery
from django.shortcuts import redirect, render

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
