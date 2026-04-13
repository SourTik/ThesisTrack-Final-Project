from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FeedbackForm, ProjectForm, SubmissionForm
from .models import Project, Submission


@login_required
def submit_project(request):
	if request.user.role != 'STUDENT':
		return HttpResponseForbidden('Only students can submit project proposals.')

	form = ProjectForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		project = form.save(commit=False)
		project.student = request.user
		project.save()
		return redirect('projects:project-list')
	return render(request, 'projects/submit_project.html', {'form': form})


@login_required
def submit_document(request, project_id):
	project = get_object_or_404(Project, id=project_id)
	if request.user.role != 'STUDENT':
		return HttpResponseForbidden('Only students can upload submission documents.')

	form = SubmissionForm(request.POST or None, request.FILES or None)
	if request.method == 'POST' and form.is_valid():
		submission = form.save(commit=False)
		submission.project = project
		submission.uploaded_by = request.user
		submission.save()
		return redirect('projects:project-list')
	return render(request, 'projects/submit_document.html', {'form': form, 'project': project})


@login_required
def approve_project(request, project_id):
	if request.user.role not in {'SUPERVISOR', 'ADMIN'}:
		return HttpResponseForbidden('Only supervisors/admin can approve projects.')

	project = get_object_or_404(Project, id=project_id)
	project.status = Project.APPROVED
	project.save(update_fields=['status', 'updated_at'])
	return redirect('projects:project-list')


@login_required
def review_submission(request, submission_id):
	if request.user.role not in {'SUPERVISOR', 'ADMIN'}:
		return HttpResponseForbidden('Only supervisors/admin can review submissions.')

	submission = get_object_or_404(Submission, id=submission_id)
	form = FeedbackForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		feedback = form.save(commit=False)
		feedback.submission = submission
		feedback.reviewer = request.user
		feedback.save()
		return redirect('projects:project-list')
	return render(request, 'projects/review_submission.html', {'form': form, 'submission': submission})


@login_required
def project_list(request):
	projects = Project.objects.all().order_by('-created_at')
	return render(request, 'projects/project_list.html', {'projects': projects})
