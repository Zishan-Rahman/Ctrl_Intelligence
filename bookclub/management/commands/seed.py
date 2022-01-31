from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from bookclub.models import User, Club

class Command(BaseCommand):
    def handle(self, *args, **options):
        faker = Faker('en_GB')

        randomUsers = []
        for i in range(0,100):

            fname = faker.first_name()
            lname = faker.last_name()
            randomEmail = f"{i}@example.org"
            randomPassw = 'Password123'
            randomBio =  "I'm new here"
            randomGenre = "Science Fiction"
            randomLocation = "London"
            randomAge = 18

            randomUser = User.objects.create_user(
                email=randomEmail,
                password=randomPassw, 
                first_name=fname, last_name=lname, 
                public_bio=randomBio, 
                favourite_genre=randomGenre, 
                location=randomLocation, 
                age=randomAge)

            randomUsers.append(randomUser)



        newClub = Club.objects.create(
            name="Bookclub1",
            location="London",
            description=faker.text(),
            owner=randomUsers[0],
            )
        newClub.organisers.add(randomUsers[1])
        newClub.members.add(randomUsers[2])



