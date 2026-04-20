from django.db import models
from django.conf import settings


class Attendance(models.Model):
	PRESENT = 'PRESENT'
	ABSENT = 'ABSENT'
	LATE = 'LATE'
	EXCUSED = 'EXCUSED'

	STATUS_CHOICES = [
		(PRESENT, 'Present'),
		(ABSENT, 'Absent'),
		(LATE, 'Late'),
		(EXCUSED, 'Excused'),
	]

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
	project = models.ForeignKey(
		'projects.Project',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='attendance_records',
	)
	date = models.DateField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PRESENT)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ('student', 'date')
		ordering = ['-date']

	def __str__(self):
		return f"{self.student} - {self.date} - {self.get_status_display()}"

	@property
	def is_present(self):
		return self.status == self.PRESENT
