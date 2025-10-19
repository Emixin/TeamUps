from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import BaseUserManager
from django.db import models




class UserQuerySet(models.QuerySet):
    def available(self):
        return self.filter(is_available=True)
    
    def is_leader(self):
        return self.filter(type="LEADER")

    def recently_added(self, days=7):
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)



class UserManager(BaseUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)
    
    def available(self):
        return self.get_queryset().available()
    
    def is_leader(self):
        return self.get_queryset().is_leader()
    
    def recently_added(self):
        return self.get_queryset().recently_added()
    


class TaskQuerySet(models.QuerySet):
    def recently_added(self, days=7):
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)



class TaskManager(models.Manager):
    def get_queryset(self):
        return TaskQuerySet(self.model, using=self._db)
    
    def recently_added(self):
        return self.get_queryset().recently_added()
    




class TeamQuerySet(models.QuerySet):
    def recently_added(self, days=7):
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)



class TeamManager(models.Manager):
    def get_queryset(self):
        return TeamQuerySet(self.model, using=self._db)
    
    def recently_added(self):
        return self.get_queryset().recently_added()
    



class InvitationQuerySet(models.QuerySet):
    def recently_added(self, days=7):
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at_gte=cutoff)



class InvitationManager(models.Manager):
    def get_queryset(self):
        return InvitationQuerySet(self.model, using=self._db)
    
    def recently_added(self):
        return self.get_queryset().recently_added()
    


class NotificationQuerySet(models.QuerySet):
    def recently_added(self, days=7):
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)



class NotificationManager(models.Manager):
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)
    
    def recently_added(self):
        return self.get_queryset().recently_added()
    