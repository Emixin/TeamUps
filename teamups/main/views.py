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
    

    def post(self, request):
        extra_time = request.POST.get("extra_time")
        task_title = request.POST.get("task_title")

        user = self.request.user
        task = Task.objects.filter(title=task_title)
        task_obj = list(task)[0]
        user_created = task_obj.created_by

        if user == user_created:
            task_obj.deadline = task_obj.renew_deadline(extra_time)
            return redirect('tasks')



class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'main/teams_list.html'
    context_object_name = 'teams'

    def get_queryset(self):
        user = self.request.user
        return Team.objects.filter(members=user)
    
    def post(self, request):
        team_name = request.POST.get("rated_team")
        team = Team.objects.filter(name=team_name)
        team_obj = list(team)[0]
        new_score = request.POST.get("score")
        team_obj.recalculate_teamwork_score(new_score)
        return redirect('teams')



class TeamDetailsView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = 'main/team_details.html'
    context_object_name = 'team'


    def post(self, request, **kwargs):
        user = request.user
        team_title = request.POST.get("title")
        team = Team.objects.filter(name=team_title)
        team_obj = list(team)[0]
        team_leader = team_obj.leader

        selected_user = request.POST.get("member")
        selected_user_qsobj = User.objects.filter(username=selected_user)
        selected_user_obj = list(selected_user_qsobj)[0]
        action = request.POST.get("action")

        team_id = kwargs.get("pk")
        if action == "add" and user == team_leader:
            team_obj.add_member(selected_user_obj)
            team_obj.save()
            return redirect('team_details', pk=team_id)

        elif action == "remove" and user == team_leader:
            team_obj.remove_member(selected_user_obj)
            team_obj.save()
            return redirect('team_details', pk=team_id)
        
        return redirect('team_details', pk=team_id)


class UsersRatingList(LoginRequiredMixin, ListView):
    model = User
    template_name = 'main/users_list.html'
    context_object_name = 'users'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.filter(is_superuser=False)
        users = users.exclude(username=self.request.user)
        context['users'] = users
        return context
    
    def post(self, request):
        new_score = request.POST.get("score")
        rated_user = request.POST.get("rated_user")

        if new_score and rated_user:
            rated_user = User.objects.filter(username=rated_user)
            rated_user_obj = list(rated_user)[0]
            rated_user_obj.score = rated_user_obj.calculate_new_score(int(new_score))
            return redirect('ratings')
            
