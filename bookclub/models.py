from django.db import models
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .custom_managers import UserManager
from django.core.validators import RegexValidator


# # Create your models here.
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
    public_bio = models.CharField(max_length=520, blank=True)
    favourite_genre = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=30, blank=False)
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

    objects = UserManager()

    USERNAME_FIELD = "email"


# Club Model adapted from Clucker user model and Chess club management system club model


class Club(models.Model):
    name = models.CharField(unique=True, blank=False, max_length=48)
    description = models.CharField(blank=True, max_length=512)
    location = models.CharField(blank=False, max_length=96)
    members = models.ManyToManyField(User, related_name="member_of")
    organisers = models.ManyToManyField(User, related_name="organiser_of")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner_of")

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

    def get_number_of_officers(self):
        return self.organisers.count()

    def get_members(self):
        return self.members.all()

    def get_organisers(self):
        return self.organisers.all()

    def get_owner(self):
        return self.owner

    def get_all_users(self):
        return (
            self.get_members()
            .union(self.get_officers())
            .union(User.objects.filter(email=self.get_owner().email))
        )

    def remove_from_club(self, user):
        if self.user_level(user) == "Member":
            self.members.remove(user)
            self.save()
        else:
            raise ValueError
