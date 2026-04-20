from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.shortcuts import redirect, render

from .forms import AdminUserCreationForm, LoginForm
from .models import User


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


def _is_admin_or_superuser(user):
	return user.is_authenticated and (user.is_superuser or user.role == User.ADMIN)


@login_required
def create_user(request):
	if not _is_admin_or_superuser(request.user):
		raise PermissionDenied('Only administrators and superusers can create users.')

	form = AdminUserCreationForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		form.save()
		return redirect('dashboard:admin-dashboard')
	return render(request, 'accounts/create_user.html', {'form': form})
