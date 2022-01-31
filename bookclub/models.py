from django.db import models
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .custom_managers import UserManager


# # Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        max_length=255,
        blank=False,
    )

    # All these field declarations are copied as-is
    # from `AbstractUser`
    first_name = models.CharField(
        max_length=30,
        blank=False,
    )
    last_name = models.CharField(
        max_length=30,
        blank=False,
    )
    is_staff = models.BooleanField(
        default=False,
        help_text=(
            'Designates whether the user can log into '
            'this admin site.'
        ),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=(
            'Designates whether this user should be '
            'treated as active. Unselect this instead '
            'of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
    )

    # Add additional fields here if needed

    # Had to remove blank=True for public_bio in order to edit it?
    public_bio = models.CharField(max_length=520)

    short_personal_statement = models.TextField()

    favourite_genre = models.CharField(max_length=520)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Club(models.Model):
    name = models.CharField(unique=True, blank=False, max_length=50)
    description = models.CharField(blank=True, max_length=500)
    location = models.CharField(blank=False, max_length=100)
    members = models.ManyToManyField(User, related_name='member_of')
    organisers = models.ManyToManyField(User, related_name='organiser_of')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_of')

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
        if self.user_level(user) == "Organiser":
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

    def add_new_member(self, user):
        self.members.add(user)
        self.save()

