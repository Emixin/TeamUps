from rest_framework import serializers
from .models import Team, Invitation, User, Task, Notification



class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["name", "leader", "max_members"]


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "skills", "type"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title", "description", "deadline", 'team', "created_by", "status"]
        

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

