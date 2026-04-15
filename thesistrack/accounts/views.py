from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy

from .models import User
from .forms import LoginForm


class ThesisTrackLoginView(LoginView):
	template_name = 'accounts/login.html'
	authentication_form = LoginForm
	redirect_authenticated_user = True

	def get_success_url(self):
		user = self.request.user
		if user.role == User.SUPERVISOR:
			return reverse_lazy('dashboard:supervisor-dashboard')
		if user.role == User.ADMIN or user.is_superuser:
			return reverse_lazy('dashboard:admin-dashboard')
		if user.role == User.STUDENT:
			return reverse_lazy('dashboard:student-dashboard')
		raise PermissionDenied('Unknown role for this user.')


class ThesisTrackLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
