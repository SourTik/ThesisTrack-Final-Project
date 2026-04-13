from django.contrib.auth.models import AbstractUser
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

	def __str__(self):
		return f"{self.username} ({self.role})"

# Create your models here.
