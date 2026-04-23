from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Team, Task
from .learning_model.matchmaker import predict_user_type


User = get_user_model()



class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        if new_password != confirm_password:
            raise forms.ValidationError("Passwords did not match!")
        return cleaned_data



class MyLoginForm(forms.Form):
    email_or_username = forms.CharField(label="Email or Username")
    password = forms.CharField(widget=forms.PasswordInput)


class MySignUpForm(UserCreationForm):
    type = forms.ChoiceField(choices=[('AI-PRED', 'AI-Pred')] + User.CHARACTER_TYPES, required=True)
    skills = forms.CharField(max_length=100, required=True)

    password1 = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}), help_text="password")
    password2 = forms.CharField(label="Confirm Password", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}), help_text="confirm password")
    
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
        self.creator = kwargs.pop('creator', None)
        super().__init__(*args, **kwargs)
        self.fields["leader"].queryset = User.objects.filter(is_superuser=False)

    def save(self, commit=True):
        team = super().save(commit=False)
        if commit:
            team.save()
            team.members.add(self.creator)
        return team
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if Team.objects.filter(name=name).exists():
            raise forms.ValidationError("A team with this name already exists!")
        return name


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'deadline', 'team', 'task_type']


    def __init__(self, *args, **kwargs):
        led_teams = kwargs.pop("user_led_teams", Team.objects.none())
        super().__init__(*args, **kwargs)
        self.fields["team"].queryset = led_teams

