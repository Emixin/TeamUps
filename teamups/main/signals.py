from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification, Task



@receiver(post_save, sender=Task)
def notify_task_creation(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.created_by, message=f"Task '{instance.title}' created!")

