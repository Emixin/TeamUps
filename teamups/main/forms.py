from django import forms


class MyLoginForm(forms.Form):
    email_or_username = forms.CharField(label="Email or Username")
    password = forms.CharField(widget=forms.PasswordInput)