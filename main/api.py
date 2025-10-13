from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from .models import Team, Invitation, User, Task, Notification

from .serializers import (
    TeamSerializer, InvitationSerializer, UserSerializer,
    TaskSerializer, NotificationSerializer
)



class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Team.objects.filter(members=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(leader=self.request.user)

    def _leadership_checker(self, team):
        if team.leader != self.request.user:
            return Response({"detail": "Only the team leader can perform this action!"}, status=status.HTTP_403_FORBIDDEN)
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
            return Response({"error": "You can only accept your own invitations."}, status=status.HTTP_403_FORBIDDEN)
        
        result = invitation.accept()
        invitation.save()
        return Response({"message": result}, status=status.HTTP_200_OK)


    def decline(self, request, pk=None):
        pass



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(created_by=self.request.user)



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

