from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.db.models import Count

from accounts.models import SupervisorStudent, User
from core.decorators import role_required
from projects.models import Project
from .forms import AttendanceMarkForm
from .models import Attendance


def _attendance_form_for_user(user, data=None):
    form = AttendanceMarkForm(data)
    if user.role == User.SUPERVISOR:
        assigned_student_ids = SupervisorStudent.objects.filter(
            supervisor=user
        ).values_list('student_id', flat=True)
        form.fields['student'].queryset = form.fields['student'].queryset.filter(id__in=assigned_student_ids)
        form.fields['project'].queryset = Project.objects.filter(student_id__in=assigned_student_ids)
    else:
        form.fields['project'].queryset = Project.objects.all()
    return form


def _apply_attendance_filters(request, queryset):
    student_id = request.GET.get('student')
    supervisor_id = request.GET.get('supervisor')
    status = request.GET.get('status')
    date = request.GET.get('date')
    project_id = request.GET.get('project')

    if student_id:
        queryset = queryset.filter(student_id=student_id)
    if supervisor_id:
        queryset = queryset.filter(supervisor_id=supervisor_id)
    if status:
        queryset = queryset.filter(status=status)
    if date:
        queryset = queryset.filter(date=date)
    if project_id:
        queryset = queryset.filter(project_id=project_id)
    return queryset


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
        if attendance.project and attendance.project.student != attendance.student:
            raise PermissionDenied('The selected project must belong to the selected student.')
        attendance.supervisor = request.user
        attendance.save()
        form = _attendance_form_for_user(request.user)
    return render(request, 'attendance/mark_attendance.html', {'form': form})


@role_required(User.STUDENT, User.SUPERVISOR, User.ADMIN)
def attendance_list(request):
    students = None
    supervisors = None
    projects = None

    if request.user.role == User.STUDENT:
        attendance_records = Attendance.objects.filter(student=request.user)
        attendance_records = _apply_attendance_filters(request, attendance_records)
        total = attendance_records.count()
        present_count = attendance_records.filter(status=Attendance.PRESENT).count()
        attendance_summary = {
            'total_sessions': total,
            'present_count': present_count,
            'absent_count': attendance_records.filter(status=Attendance.ABSENT).count(),
            'late_count': attendance_records.filter(status=Attendance.LATE).count(),
            'excused_count': attendance_records.filter(status=Attendance.EXCUSED).count(),
            'percent_present': round((present_count / total) * 100, 1) if total else 0,
        }
    elif request.user.role == User.SUPERVISOR:
        assigned_student_ids = SupervisorStudent.objects.filter(supervisor=request.user).values_list('student_id', flat=True)
        attendance_records = Attendance.objects.filter(supervisor=request.user)
        attendance_records = _apply_attendance_filters(request, attendance_records)
        attendance_summary = attendance_records.values('status').annotate(count=Count('id'))
        students = User.objects.filter(id__in=assigned_student_ids)
        projects = Project.objects.filter(student_id__in=assigned_student_ids)
    else:
        attendance_records = Attendance.objects.all()
        attendance_records = _apply_attendance_filters(request, attendance_records)
        attendance_summary = attendance_records.values('status').annotate(count=Count('id'))
        students = User.objects.filter(role=User.STUDENT)
        supervisors = User.objects.filter(role=User.SUPERVISOR)
        projects = Project.objects.all()

    return render(
        request,
        'attendance/attendance_list.html',
        {
            'attendance_records': attendance_records,
            'attendance_summary': attendance_summary,
            'students': students,
            'supervisors': supervisors,
            'projects': projects,
            'request': request,
        }
    )
