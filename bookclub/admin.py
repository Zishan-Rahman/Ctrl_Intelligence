from django.contrib import admin
from .models import User, Club, Book, Application
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
