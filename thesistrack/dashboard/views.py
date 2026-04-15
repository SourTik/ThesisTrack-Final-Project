from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from accounts.models import User
from core.decorators import role_required


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
    return render(request, 'dashboard/student_dashboard.html')


@role_required(User.SUPERVISOR)
def supervisor_dashboard(request):
    return render(request, 'dashboard/supervisor_dashboard.html')


@role_required(User.ADMIN)
def admin_dashboard(request):
    return render(request, 'dashboard/admin_dashboard.html')
