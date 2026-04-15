from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import SupervisorStudent, User


@admin.register(User)
class ThesisTrackUserAdmin(UserAdmin):
	fieldsets = UserAdmin.fieldsets + (
		('ThesisTrack', {'fields': ('role',)}),
	)
	list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
	list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')

	def _can_manage(self, request):
		return request.user.is_superuser or getattr(request.user, 'role', None) == User.ADMIN

	def has_module_permission(self, request):
		return self._can_manage(request)

	def has_view_permission(self, request, obj=None):
		return self._can_manage(request)

	def has_add_permission(self, request):
		return self._can_manage(request)

	def has_change_permission(self, request, obj=None):
		return self._can_manage(request)

	def has_delete_permission(self, request, obj=None):
		return self._can_manage(request)


@admin.register(SupervisorStudent)
class SupervisorStudentAdmin(admin.ModelAdmin):
	list_display = ('supervisor', 'student', 'assigned_by', 'created_at')
	search_fields = ('supervisor__username', 'student__username', 'assigned_by__username')
	list_filter = ('created_at',)

	def _can_manage(self, request):
		return request.user.is_superuser or getattr(request.user, 'role', None) == User.ADMIN

	def has_module_permission(self, request):
		return self._can_manage(request)

	def has_view_permission(self, request, obj=None):
		return self._can_manage(request)

	def has_add_permission(self, request):
		return self._can_manage(request)

	def has_change_permission(self, request, obj=None):
		return self._can_manage(request)

	def has_delete_permission(self, request, obj=None):
		return self._can_manage(request)
