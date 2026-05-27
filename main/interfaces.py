from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import LeaderShipInvitation, Team, Invitation, User, Task, Notification

from .serializers import (
    TeamSerializer, InvitationSerializer, UserSerializer,
    TaskSerializer, NotificationSerializer, ExtendDeadlineSerializer,
    SendTeamInvitationSerializer, RemoveMemberSerializer
)

from .pagination import NotificationViewSetPagination


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Team.objects.filter(members=self.request.user)
    
    def perform_create(self, serializer: TeamSerializer) -> None:
        team = serializer.save(leader=None)
        invited_user = serializer.validated_data["leader"]
        LeaderShipInvitation.objects.create(team=team, invited_by=self.request.user, invited_user=invited_user)
        

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
        return super().update(request, *args, **kwargs)
    
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

        if request.method == "GET":
            serializer = SendTeamInvitationSerializer()
            return Response(serializer.data)
        
        team = self.get_object()
        check_result = self._leadership_checker(team)
        if check_result:
            return check_result

        serializer = SendTeamInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        users_list = []
        search_str = serializer.validated_data["search_str"]
        if search_str:  
            searching_result = User.objects.filter(username__icontains=search_str)
            for user in searching_result:
                users_list.append((user.username, user.id))

        invited_user_id = serializer.validated_data["invited_user_id"]
        if invited_user_id == 0:
            return Response({"searching_result": users_list}, status=status.HTTP_200_OK)


        invited_user = get_object_or_404(User, id=invited_user_id)
        
        if invited_user == request.user:
            return Response({"message": "You can't invite yourself!"}, status=status.HTTP_400_BAD_REQUEST)
        
        if invited_user in team.members.all():
            return Response({"message": "You can't invite a teammate!"}, status=status.HTTP_400_BAD_REQUEST)
        
        Invitation.objects.create(team=team, invited_user=invited_user, invited_by=request.user)

        return Response({"message": "Invitation is sent!", "searching_result": users_list}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get", "post"])
    def remove_member(self, request, pk=None):

        if request.method == "GET":
            serializer = RemoveMemberSerializer()
            return Response(serializer.data)
        
        team = self.get_object()
        check_result = self._leadership_checker(team)
        if check_result:
            return check_result

        team = self.get_object()
        serializer = RemoveMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username_to_remove"]
        user = User.objects.filter(username=username).first()

        if not user in team.members.all():
            return Response({"message": "There is no such user in the team to remove!"},
                            status=status.HTTP_400_BAD_REQUEST)
        
        team.remove_member(user=user)
        return Response({"message": "User has been removed!"}, status=status.HTTP_200_OK)



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
            user = request.user
            invitation = serializer.save(invited_by=user)

            Notification.objects.create(
                user=invitation.invited_user,
                message=f"You have a new invitation from {user}!"
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

    @action(detail=True, methods=["get", "post"])
    def accept(self, request, pk=None):
        invitation = self.get_queryset().filter(id=pk)

        if not invitation.exists():
            return Response({"error": "No such invitation exists!"},
                            status=status.HTTP_404_NOT_FOUND)
        
        invitation = invitation.first()
        
        if request.user != invitation.invited_user:
            return Response({"error": "You can only accept invitations sent to you."},
                            status=status.HTTP_403_FORBIDDEN)
        
        result = invitation.accept()
        invitation.save()
        return Response({"message": result}, status=status.HTTP_200_OK)


    @action(detail=True, methods=["get", "post"])
    def decline(self, request, pk=None):
        invitation = self.get_queryset().filter(id=pk).first()

        if not invitation:
            return Response({"error": "No such invitation exists!"},
                            status=status.HTTP_404_NOT_FOUND)

        if request.user != invitation.invited_user:
            return Response({"error": "You can only decline invitations sent to you."},
                            status=status.HTTP_403_FORBIDDEN)
        
        result = invitation.decline()
        invitation.save()
        return Response({"message": result}, status=status.HTTP_200_OK)



class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)


    def perform_update(self, serializer):
        rated_user = self.get_object()
        rater_user_teams = Team.objects.filter(members=self.request.user)
        rated_user_teams = Team.objects.filter(members=rated_user)
        if not rated_user_teams.intersection(rater_user_teams).exists():
            raise ValidationError({"message": "You can only rate your teammates!"})

        rate = serializer.validated_data["score"]
        rated_user.calculate_new_score(rate)
        return super().perform_update(serializer)



class ToggleAvailabilityAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.filter(id=request.user.id).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        user.change_availability()
        return Response({"message": f"Availability changed to {user.is_available}"})



class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    filterset_fields = ['status', 'task_type']
    ordering_fields = ['deadline', 'created_at']

    def get_queryset(self):
        user_teams = Team.objects.filter(members=self.request.user)
        return Task.objects.filter(team__in=user_teams)


    @action(detail=True ,methods=["get", "post"])
    def mark_as_completed(self, request, pk=None):
        task = self.get_object()
        if task.team.leader != request.user:
            return  Response({"message": "Only team leaders can do this!"},
                             status=status.HTTP_403_FORBIDDEN)
        task.change_status()
        task.save()
        return Response({"message": "Task marked as completed!"}, status=status.HTTP_200_OK)
    


class ExtendDeadlineAPIView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, pk=None):
        task = get_object_or_404(Task, id=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)


    def post(self, request, pk=None):
        task = get_object_or_404(Task, id=pk)
        if task.team.leader != request.user:
            return Response({"message": "Only team leaders can do this!"}, status=status.HTTP_403_FORBIDDEN)
        
        if task.status == "COMPLETED":
            return Response({"message": "Task is already completed!"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ExtendDeadlineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        extra_days = serializer.validated_data["extra_days"]
        result = task.renew_deadline(extra_days)
        return Response({"message": result}, status=status.HTTP_200_OK)

        

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationViewSetPagination

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=["get", "post"])
    def mark_all_as_read(self, request):
        notifications = Notification.objects.filter(user=request.user)
        for notification in notifications:
            notification.mark_as_read()
        return Response({"message": "All notifications are marked as read!"}, status=status.HTTP_200_OK)

