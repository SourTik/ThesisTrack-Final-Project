from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from accounts.models import User
from core.decorators import role_required
from attendance.models import Attendance
from notifications.models import Notification
from projects.models import Group, Project, Submission


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
    attendance_count = Attendance.objects.filter(student=request.user).count()
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(
        request,
        'dashboard/student_dashboard.html',
        {
            'group': group,
            'project': project,
            'attendance_count': attendance_count,
            'unread_notifications': unread_notifications,
        },
    )


@role_required(User.SUPERVISOR)
def supervisor_dashboard(request):
    supervised_projects = Project.objects.filter(supervisor=request.user).select_related('group').count()
    pending_reviews = Submission.objects.filter(project__supervisor=request.user, status=Submission.PENDING).count()
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(
        request,
        'dashboard/supervisor_dashboard.html',
        {
            'supervised_projects': supervised_projects,
            'pending_reviews': pending_reviews,
            'unread_notifications': unread_notifications,
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
