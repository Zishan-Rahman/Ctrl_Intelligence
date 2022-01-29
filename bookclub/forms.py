"""Forms for the bookclub app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
#from .models import User, Post

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        #Returns authenticate user if possible

        user = None
        if self.is_valid():
            email = self.cleaned_data.get('email')
            password = self.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
        return user
