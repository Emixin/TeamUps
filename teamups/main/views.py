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
        user = self.request.user
        context["team_form"] = TeamForm()
        context["task_form"] = TaskForm(user_led_teams=Team.objects.filter(leader=user))
        return context
    
    def post(self, request):
        user = self.request.user

        if "create_task" in request.POST:
            task_form = TaskForm(request.POST, user_led_teams=Team.objects.filter(leader=user))

            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.created_by = user
                task.save()
                return redirect('dashboard')
            
        else:
            task_form = TaskForm(user_led_teams=Team.objects.filter(leader=user))

        
        if "create_team" in request.POST:
            team_form = TeamForm(request.POST)
            
            if team_form.is_valid():
                team = team_form.save()
                team.members.add(user)
                if team.leader not in team.members.all():
                    team.members.add(team.leader)
                
                return redirect('dashboard')
            
            else:
                team_form = TeamForm()
       
            context = self.get_context_data()
            context["task_form"] = task_form
            context["team_form"] = team_form
            return self.render_to_response(context)




class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'main/tasks_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        user = self.request.user
        user_teams = Team.objects.filter(members=user)
        return Task.objects.filter(team__in=user_teams)
    

# it seems the user's teams list is not correct
class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'main/teams_list.html'
    context_object_name = 'teams'

    def get_queryset(self):
        user = self.request.user
        return Team.objects.filter(members=user)

