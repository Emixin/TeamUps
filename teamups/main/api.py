from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from .models import Team, Invitation, User, Task, Notification

from .serializers import (
    TeamSerializer, InvitationSerializer, UserSerializer,
    TaskSerializer, NotificationSerializer, ExtendDeadlineSerializer,
    SendTeamInvitationSerializer
)



class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Team.objects.filter(members=self.request.user)
    
    def perform_create(self, serializer: TeamSerializer) -> None:
        serializer.save(leader=self.request.user)

    def _leadership_checker(self, team: Team) -> Response | None:
        if team.leader != self.request.user:
            return Response({"detail": "Only the team leader can perform this action!"},
                            status=status.HTTP_403_FORBIDDEN)
        return None
    
    def update(self, request, *args, **kwargs):
        team = self.get_object()
        check_result = self._leadership_checker(team)
        if check_result:
            return check_result
        return super().update(self, request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        team = self.get_object()
        check_result = self._leadership_checker(team)
        if check_result:
            return check_result
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        check_result = self._leadership_checker(team)
        if check_result:
            return check_result
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=["get", "post"])
    def send_invitation(self, request, pk=None):
        team = self.get_object()
        serializer = SendTeamInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invited_user_id = serializer.validated_data["invited_user_id"]
        invited_user = User.objects.filter(id=invited_user_id).first()
        invitation = Invitation.objects.create(team=team, invited_user=invited_user, invited_by=request.user)
        invitation.save()
        return Response({"message": "Invitation is sent!"})



class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = self.get_queryset().filter(Q(invited_user=user) | Q(invited_by=user))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            invitation = serializer.save(invited_by=request.user)

            Notification.objects.create(
                user=invitation.invited_user,
                message=f"You have a new invitation from {request.user}!"
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

    @action(detail=True, methods=["get", "post"])
    def accept(self, request, pk=None):
        invitation = self.get_queryset().filter(id=pk).first()
        
        if request.user != invitation.invited_user:
            return Response({"error": "You can only accept your own invitations."},
                            status=status.HTTP_403_FORBIDDEN)
        
        result = invitation.accept()
        invitation.save()
        return Response({"message": result}, status=status.HTTP_200_OK)


    @action(detail=True, methods=["get", "post"])
    def decline(self, request, pk=None):
        invitation = self.get_queryset().filter(id=pk).first()

        if request.user != invitation.invited_user:
            return Response({"error": "You can only decline your own invitations."},
                            status=status.HTTP_403_FORBIDDEN)
        
        result = invitation.decline()
        invitation.save()
        return Response({"message": result}, status=status.HTTP_200_OK)



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


    def perform_update(self, serializer):
        user = self.get_object()
        if self.request.user == user:
            raise ValidationError({"message": "You can't rate yourself!"})
        
        rater_teams = Team.objects.filter(members=self.request.user)
        rated_teams = Team.objects.filter(members=user)
        if not rated_teams.intersection(rater_teams).exists():
            raise ValidationError({"message": "You can only rate your teammates!"})

        rate = serializer.validated_data["score"]
        user.calculate_new_score(rate)
        user.save()
        return super().perform_update(serializer)
    

    @action(detail=True, methods=["get", "post"])
    def toggle_availability(self, request, pk=None):
        user = self.get_object()
        user.change_availability()
        return Response({"message": f"Availability changed to {user.is_available}"})



class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user)


    @action(detail=True ,methods=["get", "post"])
    def mark_as_completed(self, request, pk=None):
        task = self.get_object()
        if task.team.leader != self.request.user:
            return  Response({"message": "Only team leaders can do this!"},
                             status=status.HTTP_403_FORBIDDEN)
        task.change_status()
        task.save()
        return Response({"message": "Task marked as completed!"},
                        status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get", "post"])
    def extend_deadline(self, request, pk=None):
        task = self.get_object()
        if task.team.leader != self.request.user:
            return Response({"message": "Only team leaders can do this!"})
        if task.status == "COMPLETED":
            return Response({"message": "Task is already completed!"})
        serializer = ExtendDeadlineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        extra_days = serializer.validated_data["extra_days"]
        result = task.renew_deadline(extra_days)
        return Response({"message": {result}},
                        status=status.HTTP_200_OK)

        


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        notifications = Notification.objects.filter(user=self.request.user).all()
        for notification in notifications:
            notification.mark_as_read()
            notification.save()
        return super().perform_update(serializer)
    
    @action(detail=False, methods=["get", "post"])
    def mark_all_as_read(self, request):
        notifications = Notification.objects.filter(user=request.user)
        for notification in notifications:
            notification.mark_as_read()
            notification.save()
        return Response({"message": "All notifications are marked as read!"})
    


class NotificationDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, pk=None):
        notification = get_object_or_404(Notification, id=pk, invited_user=request.user)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)


    def post(self, request, pk=None):
        notification = get_object_or_404(Notification, id=pk)
        notification.mark_as_read()
        notification.save()
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

