from django import forms

from .models import ThesisDeadline


class ThesisDeadlineForm(forms.ModelForm):
	class Meta:
		model = ThesisDeadline
		fields = ['title', 'deadline_type', 'project', 'due_date', 'description']
		widgets = {
			'title': forms.TextInput(attrs={'class': 'w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-700 shadow-sm focus:border-[#800000] focus:ring-2 focus:ring-[#800000]/10'}),
			'deadline_type': forms.Select(attrs={'class': 'w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-700 shadow-sm focus:border-[#800000] focus:ring-2 focus:ring-[#800000]/10'}),
			'project': forms.Select(attrs={'class': 'w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-700 shadow-sm focus:border-[#800000] focus:ring-2 focus:ring-[#800000]/10'}),
			'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-700 shadow-sm focus:border-[#800000] focus:ring-2 focus:ring-[#800000]/10'}),
			'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-700 shadow-sm focus:border-[#800000] focus:ring-2 focus:ring-[#800000]/10'}),
		}