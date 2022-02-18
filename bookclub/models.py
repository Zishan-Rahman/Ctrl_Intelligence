from django.db import models
from django.forms import CharField, DateField, IntegerField
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .custom_managers import UserManager
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from libgravatar import Gravatar


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255, blank=False)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    is_staff = models.BooleanField(
        default=False,
        help_text=("Designates whether the user can log into " "this admin site."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=(
            "Designates whether this user should be "
            "treated as active. Unselect this instead "
            "of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(default=timezone.now)
    public_bio = models.CharField(max_length=512, blank=True)
    favourite_genre = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=96, blank=False)
    age = models.IntegerField(blank=True, null=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_email(self):
        return self.email

    def get_bio(self):
        return self.public_bio

    def get_favourite_genre(self):
        return self.favourite_genre

    def get_location(self):
        return self.location

    def get_age(self):
        return self.age

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    objects = UserManager()

    USERNAME_FIELD = "email"


# books model


class Book(models.Model):
    isbn = models.CharField(unique=True, max_length=12, blank=False)
    title = models.CharField(unique=False, blank=False, max_length=512)
    author = models.CharField(blank=False, max_length=512)
    pub_year = models.IntegerField(blank=False, validators=[MinValueValidator(1800), MaxValueValidator(2022)])
    publisher = models.CharField(blank=False, max_length=512)
    small_url = models.URLField(unique=False, blank=False, max_length=512)
    medium_url = models.URLField(unique=False, blank=False, max_length=512)
    large_url = models.URLField(unique=False, blank=False, max_length=512)

    def get_isbn(self):
        return self.isbn

    def get_title(self):
        return self.title

    def get_pub_year(self):
        return self.pub_year

    def get_pub_company(self):
        return self.publisher

    def get_small_url(self):
        return self.small_url

    def get_medium_url(self):
        return self.medium_url

    def get_large_url(self):
        return self.large_url


# Club Model adapted from Clucker user model and Chess club management system club model


class Club(models.Model):
    name = models.CharField(unique=True, blank=False, max_length=48)
    description = models.CharField(blank=True, max_length=512)
    location = models.CharField(blank=False, max_length=96)
    members = models.ManyToManyField(User, related_name="member_of")
    organisers = models.ManyToManyField(User, related_name="organiser_of")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner_of")
    meeting_online = models.BooleanField(unique=False, blank=False, default=True)

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_location(self):
        return self.location

    def user_level(self, user):
        if self.owner == user:
            return "Owner"
        elif self.organisers.filter(email=user.email):
            return "Organiser"
        elif self.members.filter(email=user.email):
            return "Member"
        else:
            return "Not in club"

    def make_owner(self, user):
        if self.user_level(user) == "Member":
            self.members.remove(user)
            self.organisers.add(self.owner)
            self.owner = user
            self.save()

        elif self.user_level(user) == "Organiser":
            self.organisers.remove(user)
            self.organisers.add(self.owner)
            self.owner = user
            self.save()
        else:
            raise ValueError

    def make_organiser(self, user):
        if self.user_level(user) == "Member":
            self.members.remove(user)
            self.organisers.add(user)
            self.save()
        else:
            raise ValueError

    def make_member(self, user):
        self.members.add(user)
        self.save()

    def get_number_of_members(self):
        return self.members.count()

    def get_number_organisers(self):
        return self.organisers.count()

    def get_members(self):
        return self.members.all()

    def get_organisers(self):
        return self.organisers.all()

    def get_owner(self):
        return self.owner

    def meeting_type(self):
        if self.meeting_online:
            return "online"
        return "in person"

    def get_all_users(self):
        return (
            self.get_members()
                .union(self.get_organisers())
                .union(User.objects.filter(email=self.get_owner().email))
        )

    def remove_from_club(self, user):
        if self.user_level(user) == "Member":
            self.members.remove(user)
            self.save()
        else:
            raise ValueError

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.name)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)


class Application(models.Model):
    """A model for denoting and storing applications made by users to join book clubs."""
    applicant = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, blank=False, on_delete=models.CASCADE)

    def get_applicant(self):
        return self.applicant

    def get_application_club(self):
        return self.club


# Ratings model
class Rating(models.Model):
    """A model for the book ratings"""
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=12, blank=False)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], blank=False)

    def get_user(self):
        return self.user

    def get_isbn(self):
        return self.isbn

    def get_rating(self):
        return self.rating


class Meeting(models.Model):
    """A model for denoting and storing meetings."""
    date = models.DateField()
    time = models.TimeField()
    club = models.ForeignKey(Club, blank=False, on_delete=models.CASCADE)

    def get_meeting_club(self):
        return self.club

    def get_meeting_date(self):
        return self.date

    def get_meeting_time(self):
        return self.time