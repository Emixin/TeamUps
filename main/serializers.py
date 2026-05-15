from rest_framework import serializers
from .models import Team, Invitation, User, Task, Notification



class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["name", "max_members", "leader"]


class SendTeamInvitationSerializer(serializers.Serializer):
    invited_user_id = serializers.IntegerField(min_value=1)


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ["team", "invited_user"]

    
class RemoveMemberSerializer(serializers.Serializer):
    username_to_remove = serializers.CharField()

# FIXME: UserSerializer allows writing to email and score fields
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "skills", "type", "score", "is_available"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title", "description", "deadline", 'team', "created_by", "status", "task_type", "created_at"]


class ExtendDeadlineSerializer(serializers.Serializer):
    extra_days = serializers.IntegerField(min_value=1)
        

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

