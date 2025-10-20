from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import BaseUserManager
from django.db import models



class RecentlyAddedMixin:
    def recently_added(self, days=7):
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)





class UserQuerySet(models.QuerySet, RecentlyAddedMixin):
    def available(self):
        return self.filter(is_available=True)


class UserManager(BaseUserManager.from_queryset(UserQuerySet)):
    pass
    




class TaskQuerySet(models.QuerySet, RecentlyAddedMixin):
    pass


class TaskManager(models.Manager.from_queryset(TaskQuerySet)):
    pass
    




class TeamQuerySet(models.QuerySet, RecentlyAddedMixin):
    pass


class TeamManager(models.Manager.from_queryset(TeamQuerySet)):
    pass

