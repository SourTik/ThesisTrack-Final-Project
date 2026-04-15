from django.db import models
from django.conf import settings


class Notification(models.Model):
	APPROVAL = 'APPROVAL'
	FEEDBACK = 'FEEDBACK'
	DEADLINE = 'DEADLINE'
	GENERAL = 'GENERAL'

	CATEGORY_CHOICES = [
		(APPROVAL, 'Approval'),
		(FEEDBACK, 'Feedback'),
		(DEADLINE, 'Deadline'),
		(GENERAL, 'General'),
	]

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='notifications',
	)
	title = models.CharField(max_length=120)
	message = models.TextField()
	category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=GENERAL)
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.title} -> {self.user.username}"
