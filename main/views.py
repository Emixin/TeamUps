from django.views.generic import ListView, FormView, DetailView
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages 
from django.urls import reverse_lazy
from .models import Task, Team
from .forms import MyLoginForm
from .models import User
from django.shortcuts import redirect




User = get_user_model()


class HomePageView(DetailView):
    model = User
    template_name = "main/home.html"

    def get_object(self):
        return self.request.user


class MyLoginView(FormView):
    template_name = "main/login.html"
    form_class = MyLoginForm

    def form_valid(self, form):
        username_or_email = form.cleaned_data["email_or_username"]
        password = form.cleaned_data["password"]

        try:
            user_obj = User.objects.get(email=username_or_email)
            username = user_obj.username

        except User.DoesNotExist:
            username = username_or_email

        user = authenticate(self.request, username=username, password=password)

        if user:
            login(self.request, user)
            messages.success(self.request, f"Welcome {user.username}")
            return redirect('home')


        messages.error(self.request, "Incorrect username or password")
        return self.form_invalid(form)



class MyLogoutView(LogoutView):
    next_page = reverse_lazy("home")



class DashboardView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'main/dashboard.html'
    context_object_name = 'user'



class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'main/tasks_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        user = self.request.user
        user_team = Team.objects.filter(members=user)
        return Task.objects.filter(team__in=user_team)

