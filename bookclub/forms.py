"""Forms for the bookclub app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from bookclub.models import User, Club, Application, Meeting, Post ,UserPost
from datetime import datetime
from django.utils import timezone


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'email', 'public_bio', 'favourite_genre', 'location', 'age']
        widgets = {'public_bio': forms.Textarea()}


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

class ClubForm(forms.ModelForm):
    """Form enabling users to create a new club"""
    class Meta:
        model = Club
        fields = ['name', 'description', 'location', 'meeting_type', 'organiser_has_owner_privilege']
        widgets = {"description": forms.Textarea()}

    CHOICES = [
        (None, 'Choose meeting type'),
        (True, 'Online'),
        (False, 'In Person')]

    meeting_type = forms.ChoiceField(choices=CHOICES, widget=forms.Select(), help_text="Select whether your club is "
                                                                                       "online based or meets in "
                                                                                       "person")

    CHOICES1 = [
        (None, 'Choose organiser privilege'),
        (True, 'Yes'),
        (False, 'No')]

    organiser_has_owner_privilege = forms.ChoiceField(choices=CHOICES1, widget=forms.Select())

    def clean(self):
        super().clean()
        meeting_type = self.cleaned_data.get('meeting_type')
        organiser_has_owner_privilege = self.cleaned_data.get('organiser_has_owner_privilege')

    def save(self, user):
        super().save(commit=False)
        club = Club.objects.create(
            name=self.cleaned_data.get('name'),
            description=self.cleaned_data.get('description'),
            location=self.cleaned_data.get('location'),
            owner=user,
            meeting_online=self.cleaned_data.get('meeting_type'),
            organiser_owner=self.cleaned_data.get('organiser_has_owner_privilege')
        )
        return club

class DateInput(forms.DateInput):
    """Class to have calendar on date input"""
    input_type = 'date'


class TimeInput(forms.DateInput):
    """Class to have clock on time input"""
    input_type = 'time'


class ScheduleMeetingForm(forms.ModelForm):
    """Form enabling users to schedule a new meeting in a club"""
    class Meta:
        model = Meeting
        fields = ['date', 'start_time', 'address']
        widgets = {'date': DateInput(), 'start_time': TimeInput()}

    def __init__(self, club, *args, **kwargs):
        """Construct new form instance with a user instance."""
        self.club = club
        super(ScheduleMeetingForm, self).__init__(**kwargs)
        if self.club != None and self.club.meeting_type() == "in person":
            self.fields['address'].label = 'Meeting address'
        elif self.club != None and self.club.meeting_type() == "online":
            self.fields['address'].label = 'Meeting link'

    def clean(self):
        """Clean data and make sure time is not in the past"""
        now = timezone.now()
        date = self.cleaned_data['date']
        start_time = self.cleaned_data['start_time']
        if date < datetime.now().date():
            raise forms.ValidationError("The meeting cannot be in the past!")
        elif date == datetime.now().date() and start_time < datetime.now().time():
            raise forms.ValidationError("The meeting cannot be in the past!")

    def save(self, club):
        """Save new meeting"""
        super().save(commit=False)
        meeting = Meeting.objects.create(date=self.cleaned_data.get('date'),
                                         start_time=self.cleaned_data.get('start_time'), club=club,
                                         address=self.cleaned_data.get('address'))
        return meeting


# Chat and message forms adapted from https://legionscript.medium.com/building-a-social-media-app-with-django-and-python-part-14-direct-messages-pt-1-1a6b8bd9fc40
class ChatForm(forms.Form):
    """Form enabling users to create a new chat with another user"""
    email = forms.CharField(label='', max_length=100)


class MessageForm(forms.Form):
    """Form enabling users to write a message in an already existing chat"""
    message = forms.CharField(label='', max_length=1000)


class EditClubForm(forms.ModelForm):
    """Form to update clubs."""

    class Meta:
        """Form options."""

        model = Club
        fields = ['name', 'description', 'location', 'meeting_online', 'organiser_owner']
        widgets = {'description': forms.Textarea()}

    CHOICES = [
        (None, 'Choose meeting type'),
        (True, 'Online'),
        (False, 'In Person')]

    ORGANISER_OWNER_CHOICES = [
        (True, 'Organiser has greater privileges'),
        (False, 'Organiser does not have greater privileges')
    ]

    meeting_online = forms.ChoiceField(choices=CHOICES, widget=forms.Select(), help_text="Select whether your club is "
                                                                                         "online based or meets in "
                                                                                         "person")
    organiser_owner = forms.ChoiceField(choices=ORGANISER_OWNER_CHOICES)


class PostForm(forms.ModelForm):
    """Form to ask user for post text for club posts.
    The post author must be by the post creator."""

    class Meta:
        """Form options."""

        model = Post
        fields = ['text']
        widgets = {
            'text': forms.Textarea()
        }



class UserPostForm(forms.ModelForm):
    """Form to ask user for post text for profile posts.
    The post author must be by the post creator."""
    class Meta:
        """Form options."""

        model = UserPost
        fields = ['text']
        widgets = {
            'text': forms.Textarea()
        }



