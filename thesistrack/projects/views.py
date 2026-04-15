from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import SupervisorStudent, User
from core.decorators import role_required
from notifications.models import Notification
from .forms import FeedbackForm, ProjectForm, SubmissionForm
from .models import Project, Submission


def _project_visible_to_user(user):
	if user.role == User.STUDENT:
		return Project.objects.filter(student=user)
	if user.role == User.SUPERVISOR:
		return Project.objects.filter(
			Q(supervisor=user) | Q(student__supervisor_assignments__supervisor=user)
		).distinct()
	if user.role == User.ADMIN:
		return Project.objects.all()
	return Project.objects.none()


def _can_supervisor_manage_project(user, project):
	if user.role == User.ADMIN:
		return True
	if user.role != User.SUPERVISOR:
		return False
	if project.supervisor_id == user.id:
		return True
	return SupervisorStudent.objects.filter(supervisor=user, student=project.student).exists()


@role_required(User.STUDENT)
def submit_project(request):
	form = ProjectForm(request.POST or None, user=request.user)
	if request.method == 'POST' and form.is_valid():
		project = form.save(commit=False)
		project.student = request.user
		if not project.supervisor_id:
			assignment = SupervisorStudent.objects.filter(student=request.user).first()
			if assignment:
				project.supervisor = assignment.supervisor
		project.save()
		if project.supervisor:
			Notification.objects.create(
				user=project.supervisor,
				title='New Project Proposal',
				message=f'{request.user.username} submitted project proposal "{project.title}".',
				category=Notification.GENERAL,
			)
		return redirect('projects:project-list')
	return render(request, 'projects/submit_project.html', {'form': form})


@role_required(User.STUDENT)
def submit_document(request, project_id):
	project = get_object_or_404(Project, id=project_id, student=request.user)
	form = SubmissionForm(request.POST or None, request.FILES or None)
	if request.method == 'POST' and form.is_valid():
		submission = form.save(commit=False)
		submission.project = project
		submission.uploaded_by = request.user
		submission.save()
		if project.supervisor:
			Notification.objects.create(
				user=project.supervisor,
				title='New Chapter Submission',
				message=f'{request.user.username} uploaded a .docx submission for "{project.title}".',
				category=Notification.GENERAL,
			)
		return redirect('projects:project-list')
	return render(request, 'projects/submit_document.html', {'form': form, 'project': project})


@role_required(User.SUPERVISOR, User.ADMIN)
def approve_project(request, project_id):
	project = get_object_or_404(Project, id=project_id)
	if not _can_supervisor_manage_project(request.user, project):
		raise PermissionDenied('You are not allowed to approve this project.')
	project.status = Project.APPROVED
	project.save(update_fields=['status', 'updated_at'])
	Notification.objects.create(
		user=project.student,
		title='Project Approved',
		message=f'Your proposal "{project.title}" has been approved.',
		category=Notification.APPROVAL,
	)
	return redirect('projects:project-list')


@role_required(User.SUPERVISOR, User.ADMIN)
def review_submission(request, submission_id):
	submission = get_object_or_404(Submission, id=submission_id)
	if not _can_supervisor_manage_project(request.user, submission.project):
		raise PermissionDenied('You are not allowed to review this submission.')
	form = FeedbackForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		feedback = form.save(commit=False)
		feedback.submission = submission
		feedback.reviewer = request.user
		feedback.save()
		Notification.objects.create(
			user=submission.uploaded_by,
			title='Submission Feedback Available',
			message=f'New feedback has been added for "{submission.project.title}".',
			category=Notification.FEEDBACK,
		)
		return redirect('projects:project-list')
	return render(request, 'projects/review_submission.html', {'form': form, 'submission': submission})


@login_required
def project_list(request):
	projects = _project_visible_to_user(request.user).order_by('-created_at')
	if request.user.role == User.STUDENT:
		for project in projects:
			if project.deadline:
				Notification.objects.get_or_create(
					user=request.user,
					title='Project Deadline',
					message=f'Deadline for "{project.title}" is {project.deadline}.',
					category=Notification.DEADLINE,
				)
	return render(request, 'projects/project_list.html', {'projects': projects})
