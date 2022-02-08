from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from bookclub.models import User, Club
import csv

class Command(BaseCommand):
    faker = Faker('en_GB')

    def handle(self, *args, **options):
        """ Loads the given dataset into the database"""
        self.load_users()

    def load_users(self):
        count = 1
        file_path_users = "data/BX-Users.csv"

        with open(file_path_users, encoding='cp1252') as user_csv_file:
            data = csv.reader(user_csv_file, delimiter=";")
            next(data)
            users = []
            for row in data:
                id = int(row[0])
                first_name = self.faker.first_name()
                last_name = self.faker.last_name()
                email = f'{first_name.lower()}.{last_name.lower()}{id}@example.org'
                location = row[1]
                age = row[2]
                public_bio = self.faker.text(max_nb_chars=512)
                password = "pbkdf2_sha256$260000$EoTovTO51J1EMhVCgfWM0t$jQjs11u15ELqQDNthGsC+vdLoDJRn2LDjU2qE7KqKj0="

                if age == 'NULL':
                    age = None

                user = User(
                    id=id,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    location=location,
                    age=age,
                    public_bio=public_bio,
                    email=email
                )

                users.append(user)

                count += 1
                percent_complete = float((count/278859)*100)

                print(f'DONE: {round(percent_complete)}% | {count}/278859', end='\r')
                if len(users) > 5000:
                    User.objects.bulk_create(users)
                    users = []

            if users:
                User.objects.bulk_create(users)
            print()
            print("Users successfully seeded!")



