from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from bookclub.models import User, Club, Book
import csv


class Command(BaseCommand):
    """Seeder to populate database"""

    TOTAL_USERS_IN_DATASET = 278859
    TOTAL_BOOKS_IN_DATASET = 271380
    faker = Faker('en_GB')

    def handle(self, *args, **options):
        """ Loads the given dataset into the database"""
        print()
        print('SEED USERS:')
        self.load_users()
        print('SEED DEFAULT SUPERUSER:')
        self.default_superuser()
        print('SEED BOOKS:')
        self.load_books()

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
                age = row[2]
                if age == 'NULL':
                    age = None

                user = User(
                    id=id,
                    first_name=first_name,
                    last_name=last_name,
                    password="pbkdf2_sha256$260000$EoTovTO51J1EMhVCgfWM0t$jQjs11u15ELqQDNthGsC+vdLoDJRn2LDjU2qE7KqKj0=",
                    location=row[1],
                    age=age,
                    public_bio=self.faker.text(max_nb_chars=512),
                    email=email
                )

                users.append(user)

                count += 1
                percent_complete = float((count/278859)*100)

                print(f'[ DONE: {round(percent_complete)}% | {count}/{self.TOTAL_USERS_IN_DATASET} ]', end='\r')
                if len(users) > 5000:
                    User.objects.bulk_create(users)
                    users = []

            if users:
                User.objects.bulk_create(users)
            print("The users have been successfully seeded")
            print()

    def default_superuser(self):
        User.objects.create_superuser(email="ctrl@intelligence.com", password='Password123')
        print("Default superuser created with details:")
        print("Email: ctrl@intelligence.com")
        print("Password: Password123")
        print()


    def load_books(self):
        count = 1
        file_path_users = "data/BX_Books.csv"

        with open(file_path_users, encoding='cp1252') as user_csv_file:
            data = csv.reader(user_csv_file, delimiter=";")
            next(data)
            books = []
            for row in data:
                book = Book(
                    isbn=row[0],
                    title=row[1],
                    author=row[2],
                    pub_year=row[3],
                    publisher=row[4],
                    small_url=row[5],
                    medium_url=row[6],
                    large_url=row[7]
                )
                books.append(book)
                count += 1
                percent_complete = float((count/271380)*100)

                print(f'[ DONE: {round(percent_complete)}% | {count}/{self.TOTAL_BOOKS_IN_DATASET} ]', end='\r')
                if len(books) > 5000:
                    Book.objects.bulk_create(books)
                    books = []

            if books:
                Book.objects.bulk_create(books)
            print("The books have been successfully seeded")
            print()


