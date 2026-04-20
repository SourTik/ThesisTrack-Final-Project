import os
from django import forms
from accounts.models import User
from .models import Feedback, Project, Submission

from django import forms
from accounts.models import User, SupervisorStudent # Import the assignment model
from .models import Project

from django import forms
from accounts.models import User, SupervisorStudent
from .models import Project

class ProjectForm(forms.ModelForm):
    supervisor = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.Select(attrs={
            'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500'
        }),
        required=True,
        label="Select your assigned supervisor"
    )

    class Meta:
        model = Project
        fields = ['title', 'abstract', 'supervisor']

    def __init__(self, *args, **kwargs):
        # Grab the user passed from the view
        user = kwargs.pop('user', None)
        super(ProjectForm, self).__init__(*args, **kwargs)
        
        if user:
            # 1. Find all supervisor IDs assigned to THIS student in the admin panel
            assigned_ids = SupervisorStudent.objects.filter(
                student=user
            ).values_list('supervisor_id', flat=True)
            
            # 2. Update the dropdown to show those specific users
            # Note: We removed the .filter(role='SUPERVISOR') to prevent role-name mismatches
            self.fields['supervisor'].queryset = User.objects.filter(id__in=assigned_ids)

            # 3. If the list is still empty, show ALL users for now so you can test
            if not self.fields['supervisor'].queryset.exists():
                self.fields['supervisor'].queryset = User.objects.all()
    supervisor = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.Select(attrs={
            'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500'
        }),
        required=True,
        empty_label="Select your assigned supervisor"
    )

    class Meta:
        model = Project
        fields = ['title', 'abstract', 'supervisor']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProjectForm, self).__init__(*args, **kwargs)
        
        if user:
            # Check for assignments
            assignments = SupervisorStudent.objects.filter(student=user)
            
            # DEBUG: Look at your terminal/console when you refresh the page
            print(f"DEBUG: Found {assignments.count()} assignments for user {user.username}")
            
            if assignments.exists():
                assigned_ids = assignments.values_list('supervisor_id', flat=True)
                self.fields['supervisor'].queryset = User.objects.filter(id__in=assigned_ids)
            else:
                # Fallback: If no assignment exists, show all supervisors so you aren't blocked
                # You can remove this fallback once your database is 100% correct
                self.fields['supervisor'].queryset = User.objects.filter(role='SUPERVISOR')
    supervisor = forms.ModelChoiceField(
        queryset=User.objects.none(), # Start with an empty list
        widget=forms.Select(attrs={
            'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500'
        }),
        required=True,
        label="Your Assigned Supervisor"
    )

    class Meta:
        model = Project
        fields = ['title', 'abstract', 'supervisor']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProjectForm, self).__init__(*args, **kwargs)
        
        if user:
            # Filter the dropdown to only show the supervisor assigned to this student
            assigned_supervisors = SupervisorStudent.objects.filter(student=user).values_list('supervisor_id', flat=True)
            self.fields['supervisor'].queryset = User.objects.filter(id__in=assigned_supervisors)
    supervisor = forms.ModelChoiceField(
        queryset=User.objects.filter(role='SUPERVISOR'),
        widget=forms.Select(attrs={
            'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500'
        }),
        required=True,
        label="Select a Supervisor"
    )

    class Meta:
        model = Project
        fields = ['title', 'abstract', 'supervisor']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl mb-4'}),
            'abstract': forms.Textarea(attrs={'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl mb-4', 'rows': 4}),
        }

    # This is the critical part to fix the TypeError
    def __init__(self, *args, **kwargs):
        # We "pop" the user out of the arguments so BaseModelForm doesn't see it
        self.user = kwargs.pop('user', None)
        super(ProjectForm, self).__init__(*args, **kwargs)
    # This ensures the student can only pick users who are actual Supervisors
    supervisor = forms.ModelChoiceField(
        queryset=User.objects.filter(role='SUPERVISOR'),
        widget=forms.Select(attrs={
            'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 transition'
        }),
        required=True,
        label="Select a Supervisor"
    )

    class Meta:
        model = Project
        fields = ['title', 'abstract', 'supervisor']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
                'placeholder': 'Enter project title'
            }),
            'abstract': forms.Textarea(attrs={
                'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
                'placeholder': 'Enter project abstract',
                'rows': 4
            }),
        }

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['document']
        widgets = {
            'document': forms.FileInput(attrs={
                'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl'
            }),
        }

    def clean_document(self):
        document = self.cleaned_data['document']
        extension = os.path.splitext(document.name)[1].lower()
        if extension != '.docx':
            raise forms.ValidationError('Only .docx files are allowed.')
        return document

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comments']
        widgets = {
            'comments': forms.Textarea(attrs={
                'class': 'w-full bg-slate-800 border border-slate-700 text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 transition',
                'placeholder': 'Write your feedback here...',
                'rows': 3
            }),
        }