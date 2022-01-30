from django.db import models
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
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
        _('first name'),
        max_length=30,
        blank=False,
    )
    last_name = models.CharField(
        _('last name'),
        max_length=30,
        blank=False,
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into '
            'this admin site.'
        ),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be '
            'treated as active. Unselect this instead '
            'of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
    )

    # Add additional fields here if needed

    #Had to remove blank=True for public_bio in order to edit it?
    public_bio = models.CharField(max_length=520)

    short_personal_statement = models.TextField()

    def full_name(self):
      return f'{self.first_name} {self.last_name}'

    objects = UserManager()

    USERNAME_FIELD = 'email'
