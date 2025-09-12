from django.urls import path
from .views import TaskListView, TeamListView, HomePageView, MyLoginView, MyLogoutView
from .views import DashboardView, MySignUpView


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('signup/', MySignUpView.as_view(), name='signup'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('tasks/', TaskListView.as_view(), name='tasks'),
    path('teams/', TeamListView.as_view(), name='teams'),
]
