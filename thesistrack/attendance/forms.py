from django import forms

from .models import Attendance


class AttendanceMarkForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'is_present', 'notes']