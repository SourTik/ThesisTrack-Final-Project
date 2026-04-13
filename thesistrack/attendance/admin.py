from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
	list_display = ('student', 'supervisor', 'date', 'is_present')
	list_filter = ('is_present', 'date')
	search_fields = ('student__username', 'supervisor__username')

# Register your models here.
