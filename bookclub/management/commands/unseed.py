from django.core.management.base import BaseCommand, CommandError
from bookclub.models import User, Club, Book, Rating, Application, Meeting, Chat, Message, RecommendedBook, Post, UserPost


class Command(BaseCommand):
    """Unseeder needs to delete superusers to in order to preserve the specific id's which the seeded users have"""

    def handle(self, *args, **options):

        print()

        print('Please wait, the users are being unseeded...', end='\r')
        User.objects.all().delete()
        print("[ COMPLETED: The users have successfully been unseeded ]")

        print()
        print('Please wait, the clubs are being unseeded...', end='\r')
        Club.objects.all().delete()
        print("[ COMPLETED: The clubs have successfully been unseeded ]")

        print()
        print('Please wait, the books are being unseeded...', end='\r')
        Book.objects.all().delete()
        RecommendedBook.objects.all().delete()
        print("[ COMPLETED: The books have successfully been unseeded ]")

        print()
        print('Please wait, the ratings are being unseeded...', end='\r')
        Rating.objects.all().delete()
        print("[ COMPLETED: The ratings have successfully been unseeded ]")

        print()
        print('Please wait, the applications are being unseeded...', end='\r')
        Application.objects.all().delete()
        print("[ COMPLETED: The applications have successfully been unseeded ]")

        print()
        print('Please wait, the meetings are being unseeded...', end='\r')
        Meeting.objects.all().delete()
        print("[ COMPLETED: The meetings have successfully been unseeded ]")

        print()
        print('Please wait, the chats are being unseeded...', end='\r')
        Chat.objects.all().delete()
        print("[ COMPLETED: The chats have successfully been unseeded ]")

        print()
        print('Please wait, the messages are being unseeded...', end='\r')
        Message.objects.all().delete()
        print("[ COMPLETED: The messages have successfully been unseeded ]")

        print()
        print('Please wait, the posts are being unseeded...', end='\r')
        Post.objects.all().delete()
        UserPost.objects.all().delete()
        print("[ COMPLETED: The posts have successfully been unseeded ]")
        print()
