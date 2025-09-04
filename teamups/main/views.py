from django.views.generic import ListView
from .models import Task, Team
from django.views.generic import FormView
from .forms import MyLoginForm
from .models import User
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model


User = get_user_model()


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



class TaskListView(ListView):
    model = Task
    template_name = 'main/tasks_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        user = self.request.user
        user_team = Team.objects.filter(members=user)
        return Task.objects.filter(team__in=user_team)

