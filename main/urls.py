from django.urls import path
from .views import TaskListView, TeamListView, HomePageView, MyLoginView, MyLogoutView
from .views import DashboardView, MySignUpView, UsersRatingList, TeamDetailsView, UserInvitationList


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
]
