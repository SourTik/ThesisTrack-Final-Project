from django.core.exceptions import PermissionDenied
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from core.decorators import role_required
from notifications.models import Notification
from .forms import FeedbackForm, GroupForm, ProjectForm, SubmissionForm, SupervisorAssignmentForm
from .models import Chapter, Group, Project, Submission


def _admin_recipients():
	return User.objects.filter(Q(role=User.ADMIN) | Q(is_superuser=True)).distinct()


def _notify_admins(sender, title, message):
	for admin_user in _admin_recipients():
		Notification.objects.create(
			user=admin_user,
			sender=sender,
			title=title,
			message=message,
			category=Notification.GENERAL,
		)


def _project_visible_to_user(user):
	if user.role == User.STUDENT:
		return Project.objects.filter(group__members=user).select_related('group', 'supervisor').prefetch_related('submissions__chapter')
	if user.role == User.SUPERVISOR:
		return Project.objects.filter(supervisor=user).select_related('group', 'supervisor').prefetch_related('submissions__chapter')
	if user.role == User.ADMIN:
		return Project.objects.all().select_related('group', 'supervisor').prefetch_related('submissions__chapter')
	return Project.objects.none()


def _student_group_or_403(user):
	group = Group.objects.filter(members=user).first()
	if not group:
		raise PermissionDenied('Create or join a group before performing this action.')
	return group


def _ensure_project_submission_allowed(project):
	if not project.title_approved:
		raise PermissionDenied('Title must be approved before chapter uploads.')
	if not project.supervisor_id:
		raise PermissionDenied('Supervisor must be assigned before chapter uploads.')


def _ensure_assigned_supervisor_or_403(project, user):
	if user.role != User.SUPERVISOR:
		raise PermissionDenied('Only supervisors can access this view.')
	if not project.title_approved:
		raise PermissionDenied('Project title must be approved before supervisor actions are allowed.')
	if not project.supervisor_id:
		raise PermissionDenied('No supervisor is assigned to this project yet.')
	if project.supervisor_id != user.id:
		raise PermissionDenied('You are not assigned to this project.')


def _latest_submission_for_chapter(project, chapter):
	if not chapter:
		return None
	return (
		Submission.objects.filter(project=project, chapter=chapter)
		.order_by('-version', '-submitted_at', '-id')
		.first()
	)


def _next_submission_plan(project):
	latest_submission = project.submissions.select_related('chapter').first()

	if latest_submission and latest_submission.status == Submission.PENDING:
		raise PermissionDenied('Current chapter is under review.')

	if not latest_submission:
		chapter_order = 1
	elif latest_submission.status == Submission.APPROVED:
		chapter_order = latest_submission.chapter.order + 1
	elif latest_submission.status == Submission.REJECTED:
		chapter_order = latest_submission.chapter.order
	else:
		chapter_order = 1

	chapter_name = f'Chapter {chapter_order}'
	chapter, _ = Chapter.objects.get_or_create(
		order=chapter_order,
		defaults={'name': chapter_name},
	)
	if chapter.name != chapter_name:
		chapter.name = chapter_name
		chapter.save(update_fields=['name'])

	version = (
		project.submissions.filter(chapter=chapter).aggregate(max_version=Max('version'))['max_version']
		or 0
	) + 1
	return chapter, version


@role_required(User.STUDENT)
def create_group(request):
	if Group.objects.filter(members=request.user).exists():
		raise PermissionDenied('You already belong to a group.')

	form = GroupForm(request.POST or None, user=request.user)
	if request.method == 'POST' and form.is_valid():
		group = form.save()
		_notify_admins(
			sender=request.user,
			title='Group Created',
			message=f'Group "{group.name}" was created successfully.',
		)
		return redirect('projects:project-list')
	return render(request, 'projects/create_group.html', {'form': form})


@role_required(User.STUDENT)
def submit_project(request):
	group = _student_group_or_403(request.user)
	if not group.is_valid_group():
		raise PermissionDenied('Group must contain 4-6 students before title submission.')
	if Project.objects.filter(group=group).exists():
		raise PermissionDenied('This group has already submitted a project title.')

	form = ProjectForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		project = form.save(commit=False)
		project.group = group
		project.status = Project.PENDING_TITLE
		project.title_approved = False
		project.save()
		_notify_admins(
			sender=request.user,
			title='Project Title Submitted',
			message=f'Group "{group.name}" submitted a title proposal: "{project.title}".',
		)
		return redirect('projects:project-list')
	return render(request, 'projects/submit_project.html', {'form': form, 'group': group})


@role_required(User.STUDENT)
def submit_document(request, project_id):
	project = get_object_or_404(Project, id=project_id, group__members=request.user)
	_ensure_project_submission_allowed(project)
	chapter, version = _next_submission_plan(project)

	form = SubmissionForm(request.POST or None, request.FILES or None)
	form.instance.project = project
	form.instance.uploaded_by = request.user
	form.instance.chapter = chapter
	form.instance.version = version
	if request.method == 'POST' and form.is_valid():
		submission = form.save(commit=False)
		submission.save()
		Notification.objects.create(
			user=project.supervisor,
			sender=request.user,
			title='New Chapter Submission',
			message=f'New chapter submission for "{project.title}" requires your review.',
			category=Notification.GENERAL,
		)
		return redirect('projects:project-list')
	return render(
		request,
		'projects/submit_document.html',
		{'form': form, 'project': project, 'chapter': chapter, 'version': version},
	)


@role_required(User.ADMIN)
def approve_project(request, project_id):
	project = get_object_or_404(Project, id=project_id)
	group = getattr(project, 'group', None)
	project.title_approved = True
	project.supervisor = None
	project.status = Project.TITLE_APPROVED
	project.save()

	for member in group.members.all() if group else []:
		Notification.objects.create(
			user=member,
			sender=request.user,
			title='Project Title Approved',
			message=f'Title for "{project.title}" has been approved by admin.',
			category=Notification.APPROVAL,
		)
	return redirect('projects:project-list')


@role_required(User.ADMIN)
def reject_project(request, project_id):
	project = get_object_or_404(Project, id=project_id)
	group = getattr(project, 'group', None)
	group_members = list(group.members.all()) if group else []
	project_title = project.title
	project.delete()

	for member in group_members:
		Notification.objects.create(
			user=member,
			sender=request.user,
			title='Project Title Rejected',
			message=f'Title for "{project_title}" has been rejected by admin. You can submit a new title now.',
			category=Notification.APPROVAL,
		)
	return redirect('projects:project-list')


@role_required(User.ADMIN)
def assign_supervisor(request, project_id):
	project = get_object_or_404(Project, id=project_id)
	group = getattr(project, 'group', None)
	if not project.title_approved:
		raise PermissionDenied('Title must be approved before assigning a supervisor.')

	form = SupervisorAssignmentForm(request.POST or None, instance=project)
	if request.method == 'POST' and form.is_valid():
		project = form.save(commit=False)
		project.status = Project.SUPERVISOR_ASSIGNED
		project.save()

		Notification.objects.create(
			user=project.supervisor,
			sender=request.user,
			title='Supervisor Assignment',
			message=f'You were assigned to supervise "{project.title}".',
			category=Notification.GENERAL,
		)
		for member in group.members.all() if group else []:
			Notification.objects.create(
				user=member,
				sender=request.user,
				title='Supervisor Assigned',
				message=f'A supervisor has been assigned for "{project.title}".',
				category=Notification.GENERAL,
			)
		return redirect('projects:project-list')
	return render(request, 'projects/assign_supervisor.html', {'form': form, 'project': project})


@role_required(User.SUPERVISOR)
def supervisor_assigned_projects(request):
	projects = (
		Project.objects.filter(supervisor=request.user)
		.select_related('group', 'supervisor')
		.order_by('-updated_at')
	)

	project_rows = []
	for project in projects:
		submissions = list(Submission.objects.filter(project=project).select_related('chapter'))
		submitted_chapters = len(
			{
				getattr(submission, 'chapter_id', None)
				for submission in submissions
				if getattr(submission, 'chapter_id', None)
			}
		)
		approved_submissions = [
			s for s in submissions if s.status == Submission.APPROVED and getattr(s, 'chapter_id', None)
		]
		approved_submissions.sort(
			key=lambda s: (
				getattr(s.chapter, 'order', 0),
				s.version,
				s.submitted_at,
			),
			reverse=True,
		)

		if approved_submissions and approved_submissions[0].chapter:
			current_progress = f'{approved_submissions[0].chapter.name} Approved'
		else:
			current_progress = 'No approved chapter yet'

		project_rows.append(
			{
				'project': project,
				'submitted_chapters': submitted_chapters,
				'current_progress': current_progress,
				'pending_reviews': sum(1 for s in submissions if s.status == Submission.PENDING),
			}
		)

	return render(request, 'projects/supervisor_project_list.html', {'project_rows': project_rows})


@role_required(User.SUPERVISOR)
def supervisor_project_detail(request, project_id):
	project = get_object_or_404(
		Project.objects.select_related('group', 'supervisor').prefetch_related('group__members'),
		id=project_id,
	)
	_ensure_assigned_supervisor_or_403(project, request.user)

	submissions = list(
		Submission.objects.filter(project=project)
		.select_related('chapter', 'uploaded_by')
		.prefetch_related('feedback_items__supervisor')
		.order_by('chapter__order', '-version', '-submitted_at')
	)
	group_members = list(project.group.members.all()) if project.group else []

	latest_submission_ids = set()
	seen_chapters = set()
	for submission in submissions:
		chapter_id = getattr(submission, 'chapter_id', None)
		submission_id = getattr(submission, 'pk', None)
		if chapter_id and chapter_id not in seen_chapters and submission_id is not None:
			latest_submission_ids.add(submission_id)
			seen_chapters.add(chapter_id)

	return render(
		request,
		'projects/supervisor_project_detail.html',
		{
			'project': project,
			'group_members': group_members,
			'submissions': submissions,
			'latest_submission_ids': latest_submission_ids,
		},
	)


@role_required(User.SUPERVISOR)
def review_submission(request, submission_id):
	submission = get_object_or_404(Submission, id=submission_id)
	_ensure_assigned_supervisor_or_403(submission.project, request.user)

	latest_submission = _latest_submission_for_chapter(submission.project, submission.chapter)
	latest_submission_id = getattr(latest_submission, 'pk', None)
	submission_id = getattr(submission, 'pk', None)
	if latest_submission and latest_submission_id != submission_id:
		raise PermissionDenied('Only the latest version of this chapter can be reviewed.')
	if submission.status != Submission.PENDING:
		raise PermissionDenied('This submission has already been reviewed.')

	form = FeedbackForm(request.POST or None)
	form.instance.submission = submission
	form.instance.supervisor = request.user
	if request.method == 'POST' and form.is_valid():
		decision = request.POST.get('decision')
		if decision not in {Submission.APPROVED, Submission.REJECTED}:
			form.add_error(None, 'Choose Approve or Reject for this review.')
		elif decision == Submission.REJECTED and not form.cleaned_data.get('comment', '').strip():
			form.add_error('comment', 'Feedback is required when rejecting a submission.')

		if form.errors:
			return render(request, 'projects/review_submission.html', {'form': form, 'submission': submission})

		form.save()

		submission.status = decision
		submission.reviewed_at = timezone.now()
		submission.save(update_fields=['status', 'reviewed_at'])

		group = getattr(submission.project, 'group', None)
		for member in group.members.all() if group else []:
			Notification.objects.create(
				user=member,
				sender=request.user,
				title='Submission Feedback Available',
				message=f'Feedback posted for {getattr(submission.chapter, "name", "Chapter") } in "{submission.project.title}".',
				category=Notification.FEEDBACK,
			)
		return redirect('projects:supervisor-project-detail', project_id=submission.project.pk)
	return render(request, 'projects/review_submission.html', {'form': form, 'submission': submission})


@role_required(User.STUDENT, User.SUPERVISOR, User.ADMIN)
def project_list(request):
	projects = _project_visible_to_user(request.user).order_by('-created_at')
	return render(request, 'projects/project_list.html', {'projects': projects})
