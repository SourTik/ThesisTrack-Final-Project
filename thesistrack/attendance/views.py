from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from .models import StudentAttendance, SupervisorAttendance
from .forms import StudentAttendanceForm, SupervisorAttendanceForm
from projects.models import Project

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
    
    attendance_records = SupervisorAttendance.objects.all().order_by('-date')
    
    context = {
        'attendance_records': attendance_records,
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
            attendance.save()
            messages.success(request, 'Supervisor attendance marked successfully.')
            return redirect('attendance:admin_attendance_dashboard')
    else:
        form = SupervisorAttendanceForm()

    return render(request, 'attendance/mark_attendance.html', {'form': form, 'title': 'Mark Supervisor Attendance'})


@login_required
def supervisor_attendance_dashboard(request):
    if request.user.role != 'SUPERVISOR':
        raise PermissionDenied("Only supervisors can access this page.")
    
    student_records = StudentAttendance.objects.filter(supervisor=request.user).order_by('-date')
    my_records = SupervisorAttendance.objects.filter(supervisor=request.user).order_by('-date')
    
    context = {
        'student_records': student_records,
        'my_records': my_records,
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
            except ValidationError as exc:
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
    
    attendance_records = StudentAttendance.objects.filter(student=request.user).order_by('-date')
    
    context = {
        'attendance_records': attendance_records,
    }
    return render(request, 'attendance/student_dashboard.html', context)
