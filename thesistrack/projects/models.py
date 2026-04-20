from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


class Group(models.Model):
	name = models.CharField(max_length=150, unique=True)
	members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='project_groups')
	created_at = models.DateTimeField(auto_now_add=True)

	def _members_for_validation(self):
		if hasattr(self, '_members_for_validation_cache'):
			return list(getattr(self, '_members_for_validation_cache'))
		if self.pk:
			return list(self.members.all())
		return []

	def clean(self):
		super().clean()
		members = self._members_for_validation()
		if not members:
			return

		count = len(members)
		if count < 4 or count > 6:
			raise ValidationError({'members': 'Group size must be between 4 and 6 students.'})

		for member in members:
			if member.role != 'STUDENT':
				raise ValidationError({'members': f'{member.username} is not a STUDENT.'})
			exists_in_other_group = Group.objects.filter(members=member).exclude(pk=self.pk).exists()
			if exists_in_other_group:
				raise ValidationError({'members': f'{member.username} already belongs to another group.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)

	def member_count(self):
		if hasattr(self, '_members_for_validation_cache'):
			return len(getattr(self, '_members_for_validation_cache'))
		if not self.pk:
			return 0
		return self.members.count()

	def is_valid_group(self):
		try:
			self.full_clean()
		except ValidationError:
			return False
		return True

	def __str__(self):
		return self.name


class Project(models.Model):
	PENDING_TITLE = 'PENDING_TITLE'
	TITLE_APPROVED = 'TITLE_APPROVED'
	TITLE_REJECTED = 'TITLE_REJECTED'
	SUPERVISOR_ASSIGNED = 'SUPERVISOR_ASSIGNED'
	IN_PROGRESS = 'IN_PROGRESS'
	UNDER_REVIEW = 'UNDER_REVIEW'
	COMPLETED = 'COMPLETED'

	STATUS_CHOICES = [
		(PENDING_TITLE, 'Pending Title'),
		(TITLE_APPROVED, 'Title Approved'),
		(TITLE_REJECTED, 'Title Rejected'),
		(SUPERVISOR_ASSIGNED, 'Supervisor Assigned'),
		(IN_PROGRESS, 'In Progress'),
		(UNDER_REVIEW, 'Under Review'),
		(COMPLETED, 'Completed'),
	]

	group = models.OneToOneField(
		Group,
		on_delete=models.CASCADE,
		related_name='project',
		null=True,
		blank=True,
	)
	title = models.CharField(max_length=255)
	abstract = models.TextField(blank=True)
	status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=PENDING_TITLE)
	supervisor = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='supervised_projects',
	)
	title_approved = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def clean(self):
		super().clean()
		if getattr(self, 'supervisor_id', None) and getattr(self.supervisor, 'role', None) != 'SUPERVISOR':
			raise ValidationError({'supervisor': 'Assigned user must have SUPERVISOR role.'})
		if self.status in {
			self.TITLE_APPROVED,
			self.SUPERVISOR_ASSIGNED,
			self.IN_PROGRESS,
			self.UNDER_REVIEW,
			self.COMPLETED,
		} and not self.title_approved:
			raise ValidationError({'title_approved': 'Title must be approved for this status.'})
		if self.status in {
			self.SUPERVISOR_ASSIGNED,
			self.IN_PROGRESS,
			self.UNDER_REVIEW,
			self.COMPLETED,
		} and not getattr(self, 'supervisor_id', None):
			raise ValidationError({'supervisor': 'Supervisor must be assigned for this status.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)

	def __str__(self):
		return self.title


class Chapter(models.Model):
	name = models.CharField(max_length=120, unique=True)
	order = models.PositiveIntegerField(default=1)

	class Meta:
		ordering = ['order']

	def __str__(self):
		return self.name


class Submission(models.Model):
	PENDING = 'PENDING'
	APPROVED = 'APPROVED'
	REJECTED = 'REJECTED'

	STATUS_CHOICES = [
		(PENDING, 'Pending'),
		(APPROVED, 'Approved'),
		(REJECTED, 'Rejected'),
	]

	project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='submissions')
	uploaded_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='submissions',
	)
	chapter = models.ForeignKey(
		Chapter,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='submissions',
	)
	file = models.FileField(
		upload_to='submissions/',
		validators=[FileExtensionValidator(allowed_extensions=['docx'])],
	)
	version = models.PositiveIntegerField(default=1)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
	submitted_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-submitted_at']

	def clean(self):
		super().clean()
		if not getattr(self, 'chapter_id', None):
			raise ValidationError({'chapter': 'Chapter is required for submission.'})
		chapter = getattr(self, 'chapter', None)
		if chapter and chapter.order < 1:
			raise ValidationError({'chapter': 'Chapter order must be a positive integer.'})
		if not self.project.title_approved:
			raise ValidationError('Title must be approved before chapter submission.')
		if not getattr(self.project, 'supervisor_id', None):
			raise ValidationError('Supervisor must be assigned before chapter submission.')
		if self.file and not self.file.name.lower().endswith('.docx'):
			raise ValidationError({'file': 'Only .docx files are allowed.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)

	def __str__(self):
		chapter = getattr(self, 'chapter', None)
		chapter_name = chapter.name if chapter else 'No chapter'
		return f"Submission #{self.pk} - {self.project.title} ({chapter_name})"


class Feedback(models.Model):
	submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='feedback_items')
	supervisor = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='given_feedback',
	)
	comment = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def clean(self):
		super().clean()
		project = self.submission.project
		supervisor_id = getattr(project, 'supervisor_id', None)
		if not supervisor_id:
			raise ValidationError('Submission project has no assigned supervisor.')
		if getattr(self, 'supervisor_id', None) != supervisor_id:
			raise ValidationError({'supervisor': 'Only the assigned supervisor can review this submission.'})

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)

	def __str__(self):
		return f"Feedback #{self.pk} on {self.submission.project.title}"
