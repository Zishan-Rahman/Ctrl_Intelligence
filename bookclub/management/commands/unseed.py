from django.core.management.base import BaseCommand, CommandError
from bookclub.models import User, Club, Book


class Command(BaseCommand):
    """Unseeder needs to delete superusers to in order to preserve the specific id's which the seeded users have"""

    def handle(self, *args, **options):

        User.objects.all().delete()
        print("Users successfully unseeded")

        Club.objects.all().delete()
        print("Clubs successfully unseeded")

        Book.objects.all().delete()
        print("Books successfully unseeded")
