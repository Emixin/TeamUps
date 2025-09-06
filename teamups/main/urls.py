from django.urls import path
from .views import TaskListView, HomePageView, MyLoginView, MyLogoutView, DashboardView


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view()),
    path('tasks/', TaskListView.as_view(), name='tasks'),
]
