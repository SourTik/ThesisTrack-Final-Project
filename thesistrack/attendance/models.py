from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from projects.models import Project

class StudentAttendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_attendance_records')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='marked_student_attendance')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='attendance_records', null=True, blank=True)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'project', 'date')
        ordering = ['-date', 'student__username']

    def clean(self):
        if self.student_id and self.student.role != 'STUDENT':
            raise ValidationError({'student': 'Must have STUDENT role.'})
        if self.supervisor_id and self.supervisor.role != 'SUPERVISOR':
            raise ValidationError({'supervisor': 'Must have SUPERVISOR role.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.date} ({self.get_status_display()})"


class SupervisorAttendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('INACTIVE', 'Inactive'),
    ]

    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supervisor_attendance_records')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='marked_supervisor_attendance')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('supervisor', 'date')
        ordering = ['-date', 'supervisor__username']

    def clean(self):
        if self.supervisor_id and self.supervisor.role != 'SUPERVISOR':
            raise ValidationError({'supervisor': 'Must have SUPERVISOR role.'})
        if self.admin_id and self.admin.role != 'ADMIN' and not self.admin.is_superuser:
            raise ValidationError({'admin': 'Must have ADMIN role.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.supervisor.username} - {self.date} ({self.get_status_display()})"
