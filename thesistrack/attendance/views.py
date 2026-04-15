from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from accounts.models import SupervisorStudent, User
from core.decorators import role_required
from .forms import AttendanceMarkForm
from .models import Attendance


def _attendance_form_for_user(user, data=None):
	form = AttendanceMarkForm(data)
	if user.role == User.SUPERVISOR:
		assigned_student_ids = SupervisorStudent.objects.filter(
			supervisor=user
		).values_list('student_id', flat=True)
		form.fields['student'].queryset = form.fields['student'].queryset.filter(id__in=assigned_student_ids)
	return form


@role_required(User.SUPERVISOR, User.ADMIN)
def mark_attendance(request):
	form = _attendance_form_for_user(request.user, request.POST or None)

	if request.method == 'POST' and form.is_valid():
		attendance = form.save(commit=False)
		if request.user.role == User.SUPERVISOR:
			is_assigned = SupervisorStudent.objects.filter(
				supervisor=request.user,
				student=attendance.student,
			).exists()
			if not is_assigned:
				raise PermissionDenied('You can only mark attendance for assigned students.')
		attendance.supervisor = request.user
		attendance.save()
		form = _attendance_form_for_user(request.user)
	return render(request, 'attendance/mark_attendance.html', {'form': form})


@role_required(User.STUDENT, User.SUPERVISOR, User.ADMIN)
def attendance_list(request):
	if request.user.role == User.STUDENT:
		attendance_records = Attendance.objects.filter(student=request.user)
	elif request.user.role == User.SUPERVISOR:
		attendance_records = Attendance.objects.filter(supervisor=request.user)
	else:
		attendance_records = Attendance.objects.all()
	return render(
		request,
		'attendance/attendance_list.html',
		{'attendance_records': attendance_records},
	)
