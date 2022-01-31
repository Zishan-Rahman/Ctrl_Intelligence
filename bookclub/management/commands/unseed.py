from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from bookclub.models import User, Club

class Command(BaseCommand):

    def handle(self, *args, **options):
        for user in User.objects.all():
                #if user isnt a superuser
                if not (user.is_superuser):
                    user.delete()

        for club in Club.objects.all():
                club.delete()