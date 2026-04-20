from django.db.models.signals import post_save
from django.dispatch import receiver
from projects.models import Project
from notifications.models import Notification

@receiver(post_save, sender=Project)
def notify_project_update(sender, instance, created, **kwargs):
    if created:
        # 1. Notify the Supervisor that a student submitted a project
        if instance.supervisor:
            Notification.objects.create(
                user=instance.supervisor,
                sender=instance.student,
                title="New Project Proposal",
                message=f"Student {instance.student.username} has submitted a new project: {instance.title}",
                category=Notification.APPROVAL
            )
        
        # 2. Notify the Student that their submission was successful
        Notification.objects.create(
            user=instance.student,
            sender=None, # System notification
            title="Project Submitted",
            message=f"Your project '{instance.title}' has been submitted successfully.",
            category=Notification.GENERAL
        )