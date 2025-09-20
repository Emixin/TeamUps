from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from datetime import timedelta



class User(AbstractUser):

    CHARACTER_TYPES = [
        ('LEADER', 'Leader'),
        ('SUPPORTER', 'Supporter'),
        ('THINKER', 'Thinker'),
        ('DOER', 'Doer'),
        ('CONNECTOR', 'Connector'),
    ]

    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    type = models.CharField(max_length=20, choices=CHARACTER_TYPES)
    skills = models.CharField(max_length=100, blank=True)
    score = models.DecimalField(max_digits=2, 
                                decimal_places=1, 
                                validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
                                null=True, blank=True
    )
    score_count = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)


    def calculate_new_score(self, new_score):
        self.score_count += 1
        self.score = (self.score * (self.score_count - 1) + new_score) / (self.score_count)
        self.save()
        return self.score
    
    
    def __str__(self):
        return self.username
    


class Task(models.Model):
    TASK_TYPES = [
        ('PLANNING', 'Planning'),
        ('CREATIVE', 'Creative'),
        ('TECHNICAL', 'Technical'),
        ('RESEARCH', 'Research'),
        ('TESTING', 'Testing'),
    ]

    title = models.CharField(max_length=20)
    description = models.TextField()
    deadline = models.DateTimeField()
    team = models.ForeignKey('Team', on_delete=models.CASCADE, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    status = models.CharField(max_length=20, choices=[('completed','Completed'), ('pending','PENDING')], default='PENDING')

    created_at = models.DateTimeField(auto_now_add=True)

    def renew_deadline(self, extra_time):
        extra_time = int(extra_time)
        self.deadline += timedelta(days=extra_time)
        self.save()
        return f"new deadline is {self.deadline}"
    
    def __str__(self):
        return self.title



class Team(models.Model):
    name = models.CharField(max_length=20)
    members = models.ManyToManyField(User, related_name="teams")
    max_members = models.PositiveIntegerField(default=5)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="led_teams")
    teamwork_score = models.DecimalField(max_digits=2,
                                         decimal_places=1,
                                         validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
                                         null=True, blank=True
    )
    score_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def recalculate_teamwork_score(self, new_team_score):
        self.score_count += 1
        if self.teamwork_score:
            self.teamwork_score = (self.teamwork_score * (self.score_count - 1) + int(new_team_score)) / (self.score_count)
        else:
            self.teamwork_score = new_team_score
        self.save()
        return self.teamwork_score

    def add_member(self, user):
        usersname_list = [member.username for member in self.members.all()]
        if user.username not in usersname_list and self.members.count() < self.max_members:
            self.members.add(user)
            self.save()
            return f"new user{user.username} added to team {self.name}"

    def remove_member(self, user):
        usersname_list = [member.username for member in self.members.all()]
        if user.username in usersname_list:
            self.members.remove(user)
            self.save()
            return f"the user {user.username} has been deleted!"
        
    def __str__(self):
        return self.name
    


class Invitation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='got_invitations')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def accept(self):
        if self.status == 'PENDING' and self.team.members.count() < self.team.max_members:
            self.team.add_member(self.invited_user)
            self.status = 'ACCEPTED'
            self.save()

            Notification.objects.create(user=self.invited_user, message=f"{self.invited_user} has accepted the invite to {self.team}")

            return f"user {self.invited_user} joined the team!"
        return "Invitation already handled or team is full"

    def decline(self):
        if self.status == 'PENDING':
            self.status = 'DECLINED'
            self.save()

            Notification.objects.create(user=self.invited_user, message=f"{self.invited_user} has declined the invite to {self.team}")

            return f"user {self.invited_user} declined the invitation!"
        return "Invitation already handled"



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=25)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def mark_as_read(self):
        if self.is_read == False:
            self.is_read = True
            self.save()
            return f"user {self.user} has read the notification"

