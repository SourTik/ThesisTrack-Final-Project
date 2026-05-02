from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count
from .models import StudentAttendance, SupervisorAttendance
from .forms import StudentAttendanceForm, SupervisorAttendanceForm
from projects.models import Project


def _attendance_status_breakdown(queryset, status_field='status'):
    status_counts = queryset.values(status_field).annotate(total=Count('id'))
    breakdown = {item[status_field]: item['total'] for item in status_counts}
    return {
        'present': breakdown.get('PRESENT', 0),
        'absent': breakdown.get('ABSENT', 0),
        'late': breakdown.get('LATE', 0),
        'excused': breakdown.get('EXCUSED', 0),
        'inactive': breakdown.get('INACTIVE', 0),
    }


def _attendance_trend_label(count, total):
    if not total:
        return 'No records yet'
    percentage = round((count / total) * 100)
    return f'{percentage}%'

@login_required
def attendance_list(request):
    """
    Main entry point for attendance dashboard. Routes based on user role.
    """
    if request.user.role == 'ADMIN' or request.user.is_superuser:
        return redirect('attendance:admin_attendance_dashboard')
    elif request.user.role == 'SUPERVISOR':
        return redirect('attendance:supervisor_attendance_dashboard')
    elif request.user.role == 'STUDENT':
        return redirect('attendance:student_attendance_dashboard')
    else:
        raise PermissionDenied("Invalid role.")

@login_required
def admin_attendance_dashboard(request):
    if request.user.role != 'ADMIN' and not request.user.is_superuser:
        raise PermissionDenied("Only admins can access this page.")
    
    attendance_records = SupervisorAttendance.objects.select_related('supervisor', 'admin').order_by('-date')
    record_total = attendance_records.count()
    attendance_breakdown = _attendance_status_breakdown(attendance_records)
    
    context = {
        'attendance_records': attendance_records,
        'attendance_total': record_total,
        'attendance_breakdown': attendance_breakdown,
        'recent_record': attendance_records.first(),
    }
    return render(request, 'attendance/admin_dashboard.html', context)

@login_required
def admin_mark_attendance(request):
    if request.user.role != 'ADMIN' and not request.user.is_superuser:
        raise PermissionDenied("Only admins can mark supervisor attendance.")
    
    if request.method == 'POST':
        form = SupervisorAttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.admin = request.user
            try:
                attendance.save()
            except (ValidationError, IntegrityError) as exc:
                form.add_error(None, exc)
            else:
                messages.success(request, 'Supervisor attendance marked successfully.')
                return redirect('attendance:admin_attendance_dashboard')
    else:
        form = SupervisorAttendanceForm()

    return render(request, 'attendance/mark_attendance.html', {'form': form, 'title': 'Mark Supervisor Attendance'})


@login_required
def supervisor_attendance_dashboard(request):
    if request.user.role != 'SUPERVISOR':
        raise PermissionDenied("Only supervisors can access this page.")
    
    student_records = StudentAttendance.objects.select_related('student', 'project').filter(supervisor=request.user).order_by('-date')
    my_records = SupervisorAttendance.objects.select_related('supervisor', 'admin').filter(supervisor=request.user).order_by('-date')
    student_breakdown = _attendance_status_breakdown(student_records)
    my_breakdown = _attendance_status_breakdown(my_records)
    
    context = {
        'student_records': student_records,
        'my_records': my_records,
        'student_total': student_records.count(),
        'my_total': my_records.count(),
        'student_breakdown': student_breakdown,
        'my_breakdown': my_breakdown,
        'recent_student_record': student_records.first(),
        'recent_my_record': my_records.first(),
    }
    return render(request, 'attendance/supervisor_dashboard.html', context)


@login_required
def supervisor_mark_attendance(request):
    if request.user.role != 'SUPERVISOR':
        raise PermissionDenied("Only supervisors can mark student attendance.")
    
    if request.method == 'POST':
        form = StudentAttendanceForm(request.POST, supervisor=request.user)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.supervisor = request.user

            project = Project.objects.filter(
                supervisor=request.user,
                group__members=attendance.student,
            ).first()
            if not project:
                form.add_error('student', 'Selected student has no project assigned under your supervision.')
                return render(request, 'attendance/mark_attendance.html', {'form': form, 'title': 'Mark Student Attendance'})

            attendance.project = project
            try:
                attendance.save()
            except (ValidationError, IntegrityError) as exc:
                form.add_error(None, exc)
                return render(request, 'attendance/mark_attendance.html', {'form': form, 'title': 'Mark Student Attendance'})

            messages.success(request, 'Student attendance marked successfully.')
            return redirect('attendance:supervisor_attendance_dashboard')
    else:
        form = StudentAttendanceForm(supervisor=request.user)

    return render(request, 'attendance/mark_attendance.html', {'form': form, 'title': 'Mark Student Attendance'})

@login_required
def student_attendance_dashboard(request):
    if request.user.role != 'STUDENT':
        raise PermissionDenied("Only students can access this page.")
    
    attendance_records = StudentAttendance.objects.select_related('supervisor', 'project').filter(student=request.user).order_by('-date')
    attendance_breakdown = _attendance_status_breakdown(attendance_records)
    
    context = {
        'attendance_records': attendance_records,
        'attendance_total': attendance_records.count(),
        'attendance_breakdown': attendance_breakdown,
        'recent_record': attendance_records.first(),
    }
    return render(request, 'attendance/student_dashboard.html', context)
