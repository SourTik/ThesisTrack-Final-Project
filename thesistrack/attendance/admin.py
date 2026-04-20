from django.contrib import admin
from .models import StudentAttendance, SupervisorAttendance

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'supervisor', 'project', 'date', 'status', 'created_at')
    list_filter = ('status', 'date', 'project')
    search_fields = ('student__username', 'supervisor__username', 'remarks')
    date_hierarchy = 'date'


@admin.register(SupervisorAttendance)
class SupervisorAttendanceAdmin(admin.ModelAdmin):
    list_display = ('supervisor', 'admin', 'date', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('supervisor__username', 'admin__username', 'remarks')
    date_hierarchy = 'date'
