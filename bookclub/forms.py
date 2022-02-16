"""Forms for the bookclub app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from bookclub.models import User, Club, Application

class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'email', 'public_bio', 'favourite_genre', 'location', 'age']
        widgets = { 'public_bio': forms.Textarea() }

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

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='New Password Confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""

        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(email=self.user.email, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user

      
class ApplicantForm(forms.Form):
    """Form enabling owners to choose which club applications to view."""
    applicants_dropdown = forms.ModelChoiceField(label="Select an applicant", queryset=None)

    def __init__(self, user=None, club=None, **kwargs):
        """Construct new form instance with a user instance."""

        super().__init__(**kwargs)
        self.user = user
        self.club = club

        all_applicants = Application.objects.all()
        current_applicants = []
        current_applicants_ids = []

        for a in all_applicants:
            if a.club == self.club:
                current_applicants.append(a)

        for a in current_applicants:
            current_applicants_ids.append(a.id)

        self.fields['applicants_dropdown'].queryset = Application.objects.filter(pk__in=current_applicants_ids)

  

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description', 'location']

    CHOICES = ((True, 'Online'), (False, 'In Person'))
    meeting_type = forms.ChoiceField(choices=CHOICES,widget=forms.RadioSelect)

    def clean(self):
        super().clean()
        meeting_type = self.cleaned_data.get('meeting_type')

    def save(self, user):
        super().save(commit=False)
        club = Club.objects.create(
            name = self.cleaned_data.get('name'),
            description = self.cleaned_data.get('description'),
            location = self.cleaned_data.get('location'),
            owner = user,
            meeting_online = self.cleaned_data.get('meeting_type')
        )

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = "__all__"

    def save(self):
        """Create a new application."""
        club = self.cleaned_data.get('applicants_dropdown')
        user = request.user
        app = Application.objects.create(
            club=self.cleaned_data.get('club'),
            applicant=self.cleaned_data.get('applicant'),
        )
        return app
