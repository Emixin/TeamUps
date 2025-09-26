from django.views.generic import ListView, FormView, DetailView, CreateView, TemplateView
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages 
from django.urls import reverse_lazy
from .models import Task, Team, User, Invitation, Notification
from .forms import MyLoginForm, MySignUpForm, TeamForm, TaskForm
from django.shortcuts import redirect




User = get_user_model()


class HomePageView(DetailView):
    model = User
    template_name = "main/home.html"

    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users_count'] = User.objects.filter(is_superuser=False).count()
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

    def get_success_url(self):
        return f"{reverse_lazy('user_type')}?type={self.object.type}"
    


class UserTypeView(TemplateView):
    template_name = 'main/user_type.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['predicted_user_type'] = self.request.GET.get("type")
        return context


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
                messages.success(request, "New task created!")
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
                
                messages.success(request, "New team created!")
                return redirect('dashboard')
            
            else:
                team_form = TeamForm()
       
            context = self.get_context_data()
            context["task_form"] = task_form
            context["team_form"] = team_form
            return self.render_to_response(context)



class UserInvitationList(LoginRequiredMixin, ListView):
    model = Invitation
    template_name = 'main/user_invitations.html'
    context_object_name = 'invitations'

    def get_queryset(self):
        user = self.request.user
        user_invitations = Invitation.objects.filter(invited_user=user)
        return user_invitations
    
    def post(self, request, **kwargs):
        result = request.POST.get("invitation_result")
        invitation_team = request.POST.get("invitation_team")
        invitation_team = Team.objects.filter(name=invitation_team).first()

        invited_user = request.POST.get("invited_user")
        invited_user = User.objects.filter(username=invited_user).first()


        invited_by = request.POST.get("invited_by")
        invited_by = User.objects.filter(username=invited_by).first()

        invitation = Invitation.objects.filter(team=invitation_team, invited_user=invited_user, invited_by=invited_by).first()

        if result == "accept":
            if invitation.status == "PENDING":
                invitation.accept()
                messages.success(request, "Accepted!")
            messages.error(request, "Invitation is already answered!")

        if result == "reject":
            if invitation.status == "PENDING":
                invitation.decline()
                messages.success(request, "Rejected!")
            messages.error(request, "Invitation is already answered!")
        
        invitation.save()

        user_id = kwargs.get("pk")
        return redirect('invitations', pk=user_id)




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
            messages.success(request, "Deadline is successfully changed")
            return redirect('tasks')
        messages.error(request, "You must be team leader to do that!")
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
            invitation = Invitation.objects.create(team=team_obj, invited_user=selected_user_obj, 
                                                   invited_by=team_leader)
            invitation.save()

            notification = Notification.objects.create(user=selected_user_obj, message=f"{team_leader} has invited you to {team_obj}")
            notification.save()

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

        rated_user = User.objects.filter(username=rated_user).first()
        rated_user_teams = Team.objects.filter(members=rated_user)

        user = request.user
        user_teams = Team.objects.filter(members=user)

        if new_score and rated_user and rated_user_teams.intersection(user_teams).exists():
            rated_user.score = rated_user.calculate_new_score(int(new_score))
            return redirect('ratings')
        
        messages.error(request, "You are not in the same team!")
        return redirect('ratings')
            


class NotificationsView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "main/notifications.html"
    context_object_name = "notifications"

    def get_queryset(self):
        user = self.request.user
        notifications = Notification.objects.filter(user=user)
        return notifications

