from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

from .forms import AttendanceMarkForm
from .models import Attendance


@login_required
def mark_attendance(request):
	if request.user.role not in {'SUPERVISOR', 'ADMIN'}:
		return HttpResponseForbidden('Only supervisors/admin can mark attendance.')

	form = AttendanceMarkForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		attendance = form.save(commit=False)
		attendance.supervisor = request.user
		attendance.save()
		form = AttendanceMarkForm()
	return render(request, 'attendance/mark_attendance.html', {'form': form})


@login_required
def attendance_list(request):
	if request.user.role == 'STUDENT':
		attendance_records = Attendance.objects.filter(student=request.user)
	else:
		attendance_records = Attendance.objects.all()
	return render(
		request,
		'attendance/attendance_list.html',
		{'attendance_records': attendance_records},
	)
