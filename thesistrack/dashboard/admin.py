from django.contrib import admin

from .models import ThesisDeadline


@admin.register(ThesisDeadline)
class ThesisDeadlineAdmin(admin.ModelAdmin):
	list_display = ('title', 'deadline_type', 'project', 'due_date', 'created_by', 'created_at')
	list_filter = ('deadline_type', 'due_date')
	search_fields = ('title', 'description', 'project__title')
