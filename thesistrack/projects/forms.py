import os

from django import forms

from accounts.models import User
from .models import Feedback, Project, Submission


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role == User.STUDENT:
            self.fields.pop('supervisor', None)

    class Meta:
        model = Project
        fields = ['title', 'abstract', 'supervisor']


class SubmissionForm(forms.ModelForm):
    def clean_document(self):
        document = self.cleaned_data['document']
        extension = os.path.splitext(document.name)[1].lower()
        if extension != '.docx':
            raise forms.ValidationError('Only .docx files are allowed.')
        return document

    class Meta:
        model = Submission
        fields = ['document']


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comments']