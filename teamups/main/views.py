from django.views.generic import ListView, FormView, DetailView, CreateView
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages 
from django.urls import reverse_lazy
from .models import Task, Team
from .forms import MyLoginForm, MySignUpForm, TeamForm, TaskForm
from .models import User
from django.shortcuts import redirect




User = get_user_model()


class HomePageView(DetailView):
    model = User
    template_name = "main/home.html"

    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users_count'] = User.objects.count()
        context['teams_count'] = Team.objects.count()
        context['tasks_count'] = Task.objects.count()
        return context


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
            return redirect('home')


        messages.error(self.request, "Incorrect username or password")
        return self.form_invalid(form)



class MySignUpView(CreateView):
    form_class = MySignUpForm
    template_name = 'main/signup.html'
    success_url = reverse_lazy("login")



class MyLogoutView(LogoutView):
    next_page = reverse_lazy("home")



class DashboardView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'main/dashboard.html'
    context_object_name = 'user'

    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["team_form"] = TeamForm()
        context["task_form"] = TaskForm()
        return context
 

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'main/tasks_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        user = self.request.user
        user_teams = Team.objects.filter(members=user)
        return Task.objects.filter(team__in=user_teams)
    


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.members.add(self.request.user)

        leader = form.cleaned_data["leader"]
        if leader not in self.object.members.all():
            self.object.members.add(leader)

        return response
    
    

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('dashboard')


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        task = form.save(commit=False)
        task.created_by = self.request.user
        return super().form_valid(form)

