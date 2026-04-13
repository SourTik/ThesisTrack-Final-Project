from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .forms import LoginForm


class ThesisTrackLoginView(LoginView):
	template_name = 'accounts/login.html'
	authentication_form = LoginForm

	def get_success_url(self):
		user = self.request.user
		if user.role == 'SUPERVISOR':
			return reverse_lazy('dashboard:supervisor-dashboard')
		if user.role == 'ADMIN':
			return reverse_lazy('dashboard:admin-dashboard')
		return reverse_lazy('dashboard:student-dashboard')


class ThesisTrackLogoutView(LogoutView):
	next_page = reverse_lazy('accounts:login')
