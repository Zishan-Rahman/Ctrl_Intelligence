from django.core.management.base import BaseCommand, CommandError
from bookclub.models import User, Club, Book, Rating


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
        print("[ COMPLETED: The books have successfully been unseeded ]")
        print()

        print()
        print('Please wait, the ratings are being unseeded...', end='\r')
        Rating.objects.all().delete()
        print("[ COMPLETED: The ratings have successfully been unseeded ]")
        print()
