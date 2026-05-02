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
            'username': forms.TextInput(attrs={'class': 'w-full bg-white border border-black/10 text-slate-800 px-4 py-3 rounded-xl'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full bg-white border border-black/10 text-slate-800 px-4 py-3 rounded-xl'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full bg-white border border-black/10 text-slate-800 px-4 py-3 rounded-xl'}),
            'email': forms.EmailInput(attrs={'class': 'w-full bg-white border border-black/10 text-slate-800 px-4 py-3 rounded-xl'}),
            'role': forms.Select(attrs={'class': 'w-full bg-white border border-black/10 text-slate-800 px-4 py-3 rounded-xl'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pw_class = 'w-full bg-white border border-black/10 text-slate-800 px-4 py-3 rounded-xl'
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({'class': pw_class})
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({'class': pw_class})

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.role == User.ADMIN:
            user.is_staff = True
        if commit:
            user.save()
        return user