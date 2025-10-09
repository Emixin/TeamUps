from django.urls import path, include
from .views import TaskListView, TeamListView, HomePageView, MyLoginView, MyLogoutView, UserTypeView
from .views import DashboardView, MySignUpView, UsersRatingList, TeamDetailsView, UserInvitationList, NotificationsView
from rest_framework.routers import DefaultRouter
from .api import TeamListAPIView, InvitationViewSet, UserViewSet, TaskViewSet, NotificationViewSet



router = DefaultRouter()
router.register(r'invitations', InvitationViewSet)
router.register(r'users', UserViewSet)
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'notifications', NotificationViewSet, basename='notification')



urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('signup/', MySignUpView.as_view(), name='signup'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('tasks/', TaskListView.as_view(), name='tasks'),
    path('teams/', TeamListView.as_view(), name='teams'),
    path('users/', UsersRatingList.as_view(), name='ratings'),
    path('teams/details/<int:pk>/', TeamDetailsView.as_view(), name='team_details'),
    path('user/invitations/<int:pk>/', UserInvitationList.as_view(), name='invitations'),
    path('user/notifications/<int:pk>/', NotificationsView.as_view(), name='notifications'),
    path('user/type/', UserTypeView.as_view(), name='user_type'),

    path('api/', include(router.urls)),
    path('api/teams/', TeamListAPIView.as_view()),
]
