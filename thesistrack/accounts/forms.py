from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(strip=False, widget=forms.PasswordInput)


class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl'}),
            'email': forms.EmailInput(attrs={'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl'}),
            'role': forms.Select(attrs={'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.role == User.ADMIN:
            user.is_staff = True
        if commit:
            user.save()
        return user