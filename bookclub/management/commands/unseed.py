from django.core.management.base import BaseCommand
from bookclub.models import User, Club, Book


class Command(BaseCommand):
    """The database unseeder."""

    def handle(self, *args, **options):
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        Club.objects.all().delete()