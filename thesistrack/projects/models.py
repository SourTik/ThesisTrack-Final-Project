from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings


class Project(models.Model):
	PENDING = 'PENDING'
	APPROVED = 'APPROVED'
	REJECTED = 'REJECTED'

	STATUS_CHOICES = [
		(PENDING, 'Pending'),
		(APPROVED, 'Approved'),
		(REJECTED, 'Rejected'),
	]

	title = models.CharField(max_length=255)
	abstract = models.TextField()
	student = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='owned_projects',
	)
	supervisor = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='supervised_projects',
	)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.title


class Submission(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='submissions')
	uploaded_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='submissions',
	)
	document = models.FileField(
		upload_to='submissions/',
		validators=[FileExtensionValidator(allowed_extensions=['docx'])],
	)
	submitted_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Submission #{self.pk} - {self.project.title}"


class Feedback(models.Model):
	submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='feedback_items')
	reviewer = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='given_feedback',
	)
	comments = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Feedback #{self.pk} on {self.submission.project.title}"

# Create your models here.
