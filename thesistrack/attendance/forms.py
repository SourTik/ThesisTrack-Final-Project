from django import forms

from .models import Attendance


class AttendanceMarkForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'project', 'date', 'status', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
