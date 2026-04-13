from django.db import models
from django.conf import settings


class Attendance(models.Model):
	student = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='attendance_records',
	)
	supervisor = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='marked_attendance',
	)
	date = models.DateField()
	is_present = models.BooleanField(default=False)
	notes = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('student', 'date')
		ordering = ['-date']

	def __str__(self):
		return f"{self.student} - {self.date} - {'Present' if self.is_present else 'Absent'}"

# Create your models here.
