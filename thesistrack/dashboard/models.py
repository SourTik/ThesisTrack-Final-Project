from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ThesisDeadline(models.Model):
	TITLE = 'TITLE'
	CHAPTER = 'CHAPTER'
	REVIEW = 'REVIEW'
	DEFENSE = 'DEFENSE'

	DEADLINE_TYPE_CHOICES = [
		(TITLE, 'Thesis Title'),
		(CHAPTER, 'Chapter'),
		(REVIEW, 'Thesis Review'),
		(DEFENSE, 'Thesis Defence'),
	]

	title = models.CharField(max_length=180)
	deadline_type = models.CharField(max_length=20, choices=DEADLINE_TYPE_CHOICES)
	project = models.ForeignKey(
		'projects.Project',
		on_delete=models.CASCADE,
		related_name='thesis_deadlines',
		null=True,
		blank=True,
	)
	due_date = models.DateField()
	description = models.TextField(blank=True)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='created_thesis_deadlines',
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['due_date', 'title']

	def clean(self):
		super().clean()
		creator = getattr(self, 'created_by', None)
		if creator and creator.role != 'ADMIN' and not creator.is_superuser:
			raise ValidationError({'created_by': 'Only admins can create deadlines.'})
		if self.project_id and not getattr(self.project, 'title', None):
			raise ValidationError({'project': 'Selected project is invalid.'})

	def __str__(self):
		return f'{self.title} ({self.get_deadline_type_display()})'
