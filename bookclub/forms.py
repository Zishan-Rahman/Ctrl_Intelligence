"""Forms for the bookclub app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from bookclub.models import User


class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticate user if possible"""

        user = None
        if self.is_valid():
            email = self.cleaned_data.get('email')
            password = self.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
        return user


class SignUpForm(forms.ModelForm):
    """Form enabling users to register"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase character and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()
        club_choice = self.cleaned_data.get('club_choice')

        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        """Create a new user."""
        super().save(commit=False)
        user = User.objects.create_user(
            email=self.cleaned_data.get('email'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            password=self.cleaned_data.get('new_password'),
        )
        return user
