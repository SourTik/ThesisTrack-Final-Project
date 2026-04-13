from django import forms

from .models import Feedback, Project, Submission


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'abstract', 'supervisor']


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['document']


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comments']