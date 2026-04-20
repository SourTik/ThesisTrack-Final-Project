from django.contrib import admin

from .models import Chapter, Feedback, Group, Project, Submission


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
	list_display = ('name', 'created_at', 'member_count_display')
	search_fields = ('name',)

	def member_count_display(self, obj):
		return obj.members.count()

	member_count_display.short_description = 'Members'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	list_display = ('title', 'group', 'supervisor', 'title_approved', 'status', 'created_at')
	list_filter = ('status', 'title_approved', 'created_at')
	search_fields = ('title', 'group__name', 'supervisor__username')


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
	list_display = ('project', 'chapter', 'uploaded_by', 'version', 'status', 'submitted_at')
	list_filter = ('status', 'submitted_at')
	search_fields = ('project__title', 'chapter__name', 'uploaded_by__username')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('submission', 'supervisor', 'created_at')
    search_fields = ('submission__project__title', 'supervisor__username')
