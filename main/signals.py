from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Notification, Task, Team, Invitation
from .utils import push_notification



@receiver(post_save, sender=Task)
def notify_task_creation(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.created_by, message=f"Task '{instance.title}' created!")
        push_notification(instance.created_by.username, f"Task {instance.title} created!")



@receiver(post_save, sender=Invitation)
def notify_invitation_creation(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.invited_user, message=f"You are invited to the team {instance.team}!")
        Notification.objects.create(user=instance.invited_by, message=f"You have invited user {instance.invited_user} to your team!")

