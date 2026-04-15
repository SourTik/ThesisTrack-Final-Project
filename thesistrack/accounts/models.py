from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
	STUDENT = 'STUDENT'
	SUPERVISOR = 'SUPERVISOR'
	ADMIN = 'ADMIN'

	ROLE_CHOICES = [
		(STUDENT, 'Student'),
		(SUPERVISOR, 'Supervisor'),
		(ADMIN, 'Admin'),
	]

	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)

	def save(self, *args, **kwargs):
		if self.is_superuser:
			self.role = self.ADMIN
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.username} ({self.role})"


class SupervisorStudent(models.Model):
	supervisor = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='assigned_students',
	)
	student = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='supervisor_assignments',
	)
	assigned_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='created_assignments',
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('supervisor', 'student')
		ordering = ['student__username']

	def clean(self):
		if self.supervisor_id and self.supervisor.role != User.SUPERVISOR:
			raise ValidationError({'supervisor': 'Assigned supervisor must have SUPERVISOR role.'})
		if self.student_id and self.student.role != User.STUDENT:
			raise ValidationError({'student': 'Assigned student must have STUDENT role.'})
		if self.assigned_by_id and self.assigned_by.role != User.ADMIN:
			raise ValidationError({'assigned_by': 'Assignments must be created by ADMIN users.'})

	def __str__(self):
		return f"{self.supervisor.username} -> {self.student.username}"
