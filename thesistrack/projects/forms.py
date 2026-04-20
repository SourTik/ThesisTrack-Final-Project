from django import forms
from django.db.models import Q
from accounts.models import User

from .models import Feedback, Group, Project, Submission


class GroupForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Group
        fields = ['name', 'members']

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        base_students = User.objects.filter(role=User.STUDENT).distinct()
        if self.instance.pk:
            current_member_ids = self.instance.members.values_list('id', flat=True)
            self.fields['members'].queryset = base_students.filter(
                Q(project_groups__isnull=True) | Q(id__in=current_member_ids)
            ).distinct()
        else:
            self.fields['members'].queryset = base_students.filter(project_groups__isnull=True)

        if self.request_user and self.request_user.role == User.STUDENT:
            current_selection = self.initial.get('members') or []
            if self.request_user.pk not in [m.pk if hasattr(m, 'pk') else m for m in current_selection]:
                self.initial['members'] = list(current_selection) + [self.request_user.pk]

    def clean_members(self):
        members = list(self.cleaned_data.get('members', []))
        if self.request_user and self.request_user.role == User.STUDENT and self.request_user not in members:
            members.append(self.request_user)

        member_count = len(members)
        if member_count < 4 or member_count > 6:
            raise forms.ValidationError('Group size must be between 4 and 6 students.')

        for user in members:
            if user.role != User.STUDENT:
                raise forms.ValidationError(f'{user.username} is not a STUDENT user.')

            already_grouped = Group.objects.filter(members=user)
            if self.instance.pk:
                already_grouped = already_grouped.exclude(pk=self.instance.pk)
            if already_grouped.exists():
                raise forms.ValidationError(f'{user.username} already belongs to another group.')

        return members

    def save(self, commit=True):
        members = self.cleaned_data['members']
        instance = super().save(commit=False)
        instance._members_for_validation_cache = members
        if commit:
            instance.save()
            instance.members.set(members)
            instance._members_for_validation_cache = list(instance.members.all())
            instance.full_clean()
        return instance


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'abstract']


class SupervisorAssignmentForm(forms.ModelForm):
    supervisor = forms.ModelChoiceField(queryset=User.objects.filter(role=User.SUPERVISOR))

    class Meta:
        model = Project
        fields = ['supervisor']

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']

    def clean_file(self):
        uploaded_file = self.cleaned_data['file']
        if uploaded_file and not uploaded_file.name.lower().endswith('.docx'):
            raise forms.ValidationError('Only .docx files are allowed.')
        return uploaded_file

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment']