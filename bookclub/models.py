import datetime
from django.db import models
from django.forms import CharField, DateField, IntegerField
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .custom_managers import UserManager
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from libgravatar import Gravatar


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

    class Meta:
        """Model options."""

        ordering = ['title']

    def __str__(self):
        return self.title

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
    currently_reading_books = models.ManyToManyField(Book, related_name='%(class)s_currently_reading_books')
    favourite_books = models.ManyToManyField(Book)
    is_email_verified = models.BooleanField(default=False)
    followers = models.ManyToManyField(
        'self', symmetrical=False, related_name='followees'
    )

    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

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

    def toggle_follow(self, followee):
        if followee == self:
            return
        if self.is_following(followee):
            self._unfollow(followee)
        else:
            self._follow(followee)

    def _follow(self, user):
        user.followers.add(self)

    def _unfollow(self, user):
        user.followers.remove(self)

    def is_following(self, user):
        return user in self.followees.all()

    def follower_count(self):
        return self.followers.count()

    def followee_count(self):
        return self.followees.count()

    def get_ratings(self):
        return Rating.objects.filter(user_id=self.id)

    def get_number_of_ratings(self):
        return len(self.get_ratings())

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
    meeting_online = models.BooleanField(unique=False, blank=False, default=True)
    organiser_owner = models.BooleanField(unique=False, blank=False, default=True)

    class Meta:
        """Model options."""

        ordering = ['name']

    def __str__(self):
        return self.name

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
        elif self.user_level(user) == "Organiser":
            self.organisers.remove(user)

        self.members.add(self.owner)
        self.owner = user
        self.save()

    def make_organiser(self, user):
        if self.user_level(user) == "Member":
            self.members.remove(user)
            self.organisers.add(user)
            self.save()
        else:
            raise ValueError

    def demote_organiser(self, user):
        if self.user_level(user) == "Organiser":
            self.organisers.remove(user)
            self.members.add(user)
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

    def get_meetings(self):
        return Meeting.objects.filter(club_id=self.id)

    def get_all_users(self):
        self.club_members = self.get_members()
        self.club_organisers = self.get_organisers()
        self.club_owner = User.objects.filter(email=self.get_owner().email)

        return (self.club_members | self.club_organisers | self.club_owner).distinct()

    def remove_from_club(self, user):
        if self.user_level(user) == "Member":
            self.members.remove(user)
            self.save()

        elif self.user_level(user) == "Organiser":
            self.organisers.remove(user)
            self.save()

        else:
            raise ValueError

    def organiser_has_owner_privilege(self):
        if self.organiser_owner:
            return "Organiser has owner privileges."
        else:
            return "Organiser does not have owner privileges."

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

    class Meta:
        """Model options."""

        ordering = ['applicant']

    def get_applicant(self):
        return self.applicant

    def get_application_club(self):
        return self.club


# Ratings model
class Rating(models.Model):
    """A model for the book ratings"""
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, blank=True, null=True, on_delete=models.CASCADE)
    isbn = models.CharField(unique=False, max_length=12, blank=False)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], blank=False)

    class Meta:
        """Model options."""

        ordering = ['book']

    def get_user(self):
        return self.user

    def get_book(self):
        return self.book

    def get_rating(self):
        return self.rating


class Meeting(models.Model):
    """A model for denoting and storing meetings."""
    date = models.DateField()
    start_time = models.TimeField()
    club = models.ForeignKey(Club, blank=False, on_delete=models.CASCADE)
    address = models.CharField(max_length=50, blank=False, null=False)

    class Meta:
        """Model options."""

        ordering = ['date', 'start_time']

    def get_meeting_club(self):
        return self.club

    def get_meeting_date(self):
        return self.date

    def get_meeting_start_time(self):
        return self.start_time

    def get_meeting_address(self):
        return self.address


# Chat and Message models adapted from https://legionscript.medium.com/building-a-social-media-app-with-django-and-python-part-14-direct-messages-pt-1-1a6b8bd9fc40
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    has_unread = models.BooleanField(default=False)


class Message(models.Model):
    chat = models.ForeignKey('Chat', related_name='+', on_delete=models.CASCADE, blank=True, null=True)
    sender_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    receiver_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    body = models.CharField(max_length=1000)
    date = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, blank=True, null=True)


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, blank=False, on_delete=models.CASCADE)
    text = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class RecommendedBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    isbn = models.CharField(unique=False, max_length=12, blank=False)

