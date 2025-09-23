from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Team, Task


User = get_user_model()

class MyLoginForm(forms.Form):
    email_or_username = forms.CharField(label="Email or Username")
    password = forms.CharField(widget=forms.PasswordInput)


class MySignUpForm(UserCreationForm):
    type = forms.ChoiceField(choices=User.CHARACTER_TYPES, required=True)
    skills = forms.CharField(max_length=100, required=True)

    password1 = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}), help_text="")
    password2 = forms.CharField(label="Confirm Password", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}), help_text="")

    class Meta:
        model = User
        fields = ["username", "email", "type", "skills", "password1", "password2"]

    def clean_skills(self):
        skills = self.cleaned_data.get("skills")
        if not skills or skills.strip() == "":
            raise forms.ValidationError("You must enter at least one skill")
        return skills


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

