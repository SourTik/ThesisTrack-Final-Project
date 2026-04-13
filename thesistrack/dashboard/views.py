from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render


def _role_guard(request, role):
	if request.user.role != role:
		return HttpResponseForbidden('You are not authorized to access this dashboard.')
	return None


@login_required
def home(request):
	if request.user.role == 'SUPERVISOR':
		return redirect('dashboard:supervisor-dashboard')
	if request.user.role == 'ADMIN':
		return redirect('dashboard:admin-dashboard')
	return redirect('dashboard:student-dashboard')


@login_required
def student_dashboard(request):
	blocked = _role_guard(request, 'STUDENT')
	if blocked:
		return blocked
	return render(request, 'dashboard/student_dashboard.html')


@login_required
def supervisor_dashboard(request):
	blocked = _role_guard(request, 'SUPERVISOR')
	if blocked:
		return blocked
	return render(request, 'dashboard/supervisor_dashboard.html')


@login_required
def admin_dashboard(request):
	blocked = _role_guard(request, 'ADMIN')
	if blocked:
		return blocked
	return render(request, 'dashboard/admin_dashboard.html')
