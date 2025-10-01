from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Team, Task
from .learning_model.matchmaker import predict_user_type


User = get_user_model()

class MyLoginForm(forms.Form):
    email_or_username = forms.CharField(label="Email or Username")
    password = forms.CharField(widget=forms.PasswordInput)


class MySignUpForm(UserCreationForm):
    type = forms.ChoiceField(choices=[('AI-PRED', 'AI-Pred')] + User.CHARACTER_TYPES, required=True)
    skills = forms.CharField(max_length=100, required=True)

    password1 = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}), help_text="")
    password2 = forms.CharField(label="Confirm Password", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}), help_text="")
    
    class Meta:
        model = User
        fields = ["username", "email", "skills", "password1", "password2", "type"]


    def clean_type(self):
        type_value = self.cleaned_data["type"]
        if type_value == "AI-PRED":
            skills = self.cleaned_data["skills"]
            type_value = predict_user_type(skills).upper()
        return type_value


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
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields["leader"].queryset = User.objects.filter(is_superuser=False)

    def save(self, commit=True):
        team = super().save(commit=False)
        if commit:
            team.save()
            team.members.add(self.user)
            leader = self.cleaned_data['leader']
            if leader not in team.members.all():
                team.members.add(leader)
        return team


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'deadline', 'team', 'task_type']


    def __init__(self, *args, **kwargs):
        led_teams = kwargs.pop("user_led_teams", Team.objects.none())
        super().__init__(*args, **kwargs)
        self.fields["team"].queryset = led_teams

