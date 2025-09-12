from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Team, Task


User = get_user_model()

class MyLoginForm(forms.Form):
    email_or_username = forms.CharField(label="Email or Username")
    password = forms.CharField(widget=forms.PasswordInput)


class MySignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'max_members', 'leader']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["leader"].queryset = User.objects.filter(is_superuser=False)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'deadline', 'team', 'task_type']


    def __init__(self, *args, **kwargs):
        led_teams = kwargs.pop("user_led_teams", Team.objects.none())
        super().__init__(*args, **kwargs)
        self.fields["team"].queryset = led_teams

