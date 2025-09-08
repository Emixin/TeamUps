from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()

class MyLoginForm(forms.Form):
    email_or_username = forms.CharField(label="Email or Username")
    password = forms.CharField(widget=forms.PasswordInput)


class MySignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
