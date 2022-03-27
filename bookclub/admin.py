from django.contrib import admin
from .models import User, Club, Book, Application, Post, Rating, Meeting, Chat, Message
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'first_name', 'last_name', 'email', 'location', 'age', 'is_active',
    ]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'location', 'description'
    ]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'isbn', 'title', 'author', 'pub_year'
    ]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'applicant', 'club'
    ]

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'created_at', 'author', 'club', 'text'
    ]

    def get_author(self, post):
        """Return the author of a given post."""
        return post.author.email

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'book', 'isbn', 'rating'
    ]

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = [
        'club', 'date', 'address', 'start_time'
    ]

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'receiver', 'has_unread'
    ]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'sender_user', 'receiver_user', 'club', 'chat', 'body', 'date', 'is_read'
    ]
