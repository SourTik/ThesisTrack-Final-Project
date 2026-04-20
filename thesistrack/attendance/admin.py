from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'student', 'supervisor', 'project', 'status', 'created_at')
    list_filter = ('status', 'date', 'supervisor', 'project')
    search_fields = ('student__username', 'supervisor__username', 'project__title', 'notes')
    date_hierarchy = 'date'
