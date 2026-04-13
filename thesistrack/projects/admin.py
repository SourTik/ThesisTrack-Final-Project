from django.contrib import admin

from .models import Feedback, Project, Submission


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	list_display = ('title', 'student', 'supervisor', 'status', 'created_at')
	list_filter = ('status', 'created_at')
	search_fields = ('title', 'student__username', 'supervisor__username')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
	list_display = ('project', 'uploaded_by', 'submitted_at')
	search_fields = ('project__title', 'uploaded_by__username')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
	list_display = ('submission', 'reviewer', 'created_at')
	search_fields = ('submission__project__title', 'reviewer__username')

# Register your models here.
