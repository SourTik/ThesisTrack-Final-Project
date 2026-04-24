from django import forms
from .models import StudentAttendance, SupervisorAttendance

class StudentAttendanceForm(forms.ModelForm):
    class Meta:
        model = StudentAttendance
        fields = ['student', 'date', 'status', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}),
            'student': forms.Select(attrs={'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}),
            'status': forms.Select(attrs={'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}),
            'remarks': forms.Textarea(attrs={'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        supervisor = kwargs.pop('supervisor', None)
        super().__init__(*args, **kwargs)
        if supervisor:
            from accounts.models import User
            assigned_student_ids = supervisor.assigned_students.filter(student__role=User.STUDENT).values_list('student_id', flat=True)
            if assigned_student_ids:
                self.fields['student'].queryset = User.objects.filter(id__in=assigned_student_ids)
            else:
                # No assigned students yet: show all students so the supervisor can still mark attendance.
                self.fields['student'].queryset = User.objects.filter(role=User.STUDENT)

        self.fields['student'].help_text = 'Project will be selected automatically based on the student\'s project assigned to you.'


class SupervisorAttendanceForm(forms.ModelForm):
    class Meta:
        model = SupervisorAttendance
        fields = ['supervisor', 'date', 'status', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}),
            'supervisor': forms.Select(attrs={'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}),
            'status': forms.Select(attrs={'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'}),
            'remarks': forms.Textarea(attrs={'class': 'w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import User
        self.fields['supervisor'].queryset = User.objects.filter(role=User.SUPERVISOR)
