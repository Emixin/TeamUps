from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from .utils import push_notification, get_notification_model



@receiver(post_save, sender='main.Task')
def notify_task_creation(sender, instance, created, **kwargs):
    if created:
        Notification = get_notification_model()
        Notification.objects.create(user=instance.created_by, message=f"Task '{instance.title}' created!")
        push_notification(instance.created_by.username, f"Task {instance.title} created!")



@receiver(post_save, sender='main.Invitation')
def notify_invitation_creation(sender, instance, created, **kwargs):
    if created:
        Notification = get_notification_model()
        Notification.objects.create(user=instance.invited_user, message=f"You are invited to the team {instance.team}!")



invitation_acceptence = Signal()
@receiver(invitation_acceptence)
def notify_invitation_acceptance(sender, instance, result, **kwargs):
    Notification = get_notification_model()
    Notification.objects.create(user=instance.invited_by,
                                message=f"User {instance.invited_user.username} {result} the invitation for the team {instance.team.name}")


member_removal = Signal()
@receiver(member_removal)
def notify_member_removal(sender, removed_user, team, **kwargs):
    Notification = get_notification_model()
    Notification.objects.create(user=removed_user, message=f"You are removed from the team {team.name}!")



leadership_invitation_acceptence = Signal()
@receiver(leadership_invitation_acceptence)
def notify_leadership_acceptence(sender, instance, result, **kwargs):
    Notification = get_notification_model()
    Notification.objects.create(user=instance.invited_by,
                                message=f"User {instance.invited_user.username} {result} the leadership invitaion for the team {instance.team.name}")
