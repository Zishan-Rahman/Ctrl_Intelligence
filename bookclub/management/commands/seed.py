import random

from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from bookclub.models import User, Club


def create_set_users():
    User.objects.create(
        first_name="John",
        last_name="Doe",
        email="johndoe@bookclub.com",
        public_bio="I'm just an abstract concept!",
        favourite_genre="Science fiction",
        location="London",
        age=39,
        password="pbkdf2_sha256$260000$EoTovTO51J1EMhVCgfWM0t$jQjs11u15ELqQDNthGsC+vdLoDJRn2LDjU2qE7KqKj0="
    )
    User.objects.create(
        first_name="Jane",
        last_name="Doe",
        email="janedoe@bookclub.com",
        public_bio="I'm also an abstract concept!",
        favourite_genre="Adventure",
        location="Oxford",
        age=32,
        password="pbkdf2_sha256$260000$EoTovTO51J1EMhVCgfWM0t$jQjs11u15ELqQDNthGsC+vdLoDJRn2LDjU2qE7KqKj0="
    )
    User.objects.create(
        first_name="Joe",
        last_name="Doe",
        email="joedoe@bookclub.com",
        public_bio="Just another fake user again!",
        favourite_genre="Romance",
        location="London",
        age=52,
        password="pbkdf2_sha256$260000$EoTovTO51J1EMhVCgfWM0t$jQjs11u15ELqQDNthGsC+vdLoDJRn2LDjU2qE7KqKj0="
    )


def generate_genre():
    genres = ['Action', 'Adventure', 'Romance', 'Science Fiction', 'Horror', 'Non-fiction', 'Poetry', 'Thriller',
              'Classics', 'Comics', 'Crime', 'Fantasy', 'Psychological', 'Foreign', 'Biographies', 'Religious']
    return random.choice(genres)

def generate_provider():
    providers = ['']

class Command(BaseCommand):
    faker = Faker('en_GB')

    def handle(self, *args, **options):
        print('')

    def create_user(self):
        provider = 0
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = f'{first_name}.{last_name}@{provider}.com'
        password = 'pbkdf2_sha256$260000$EoTovTO51J1EMhVCgfWM0t$jQjs11u15ELqQDNthGsC+vdLoDJRn2LDjU2qE7KqKj0='
        bio = self.faker.text(max_nb_chars=400)
        genre = generate_genre()
        location = self.faker.city()
        age = random.randint(16, 100)

        randomUser = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            public_bio=bio,
            favourite_genre=genre,
            location=location,
            age=age)

        return randomUser

    def create_club(self):
        location = self.faker.city()
        name = location + 'Book Club'
        description = self.faker.text(512)
        owner = User.objects.all().get(pk=random.randint(1, User.objects.count()))



'''
name = models.CharField(unique=True, blank=False, max_length=48)
    description = models.CharField(blank=True, max_length=512)
    location = models.CharField(blank=False, max_length=96)
    members = models.ManyToManyField(User, related_name="member_of")
    organisers = models.ManyToManyField(User, related_name="organiser_of")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner_of")
    meeting_online = models.BooleanField(unique=False, blank=False, default=True)










        newClub = Club.objects.create(
            name="Bookclub1",
            location="London",
            description=faker.text(256),
            owner=randomUsers[0],
        )
        newClub.organisers.add(randomUsers[1])
        newClub.members.add(randomUsers[2])
'''
