from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from bookclub.models import User, Club, Book, Rating
import csv
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    """Seeder to populate database"""

    TOTAL_USERS_IN_DATASET = 278859
    TOTAL_BOOKS_IN_DATASET = 271380
    faker = Faker('en_GB')

    def handle(self, *args, **options):
        """ Loads the given dataset into the database"""

        seed_possible = self.verify_seeding_possible()

        seeder_disclaimer = input("This seeder can take almost 15 minutes to complete."
                                  " If you simply need users, books and clubs then use"
                                  "seed.py. Are you sure you want to continue? Y/N").lower()

        if seeder_disclaimer != "y":
            seed_possible = False

        if seed_possible:
            print()
            print('SEED USERS:')
            self.load_users()
            print('SEED DEFAULT SUPERUSER:')
            self.default_superuser()
            print('SEED BOOKS:')
            self.load_books()
            print('SEED RATINGS')
            self.load_ratings()
        else:
            print()
            print('You have either chosen to abort the advanced seeder or...')
            print('the database must first be unseeded.')
            print('To do this, enter the command below:')
            print('> python3 manage.py unseed')
            print()

    def verify_seeding_possible(self):
        seed_possible = True
        users_present = User.objects.count()
        books_present = Book.objects.count()

        if users_present > 0:
            seed_possible = False

        if books_present > 0:
            seed_possible = False

        return seed_possible

    def load_users(self):
        count = 0
        file_path_users = "data/BX-Users.csv"

        with open(file_path_users, encoding='latin-1') as user_csv_file:
            data = csv.reader(user_csv_file, delimiter=";")
            next(data)
            users = []
            for row in data:
                user_id = int(row[0])
                first_name = self.faker.first_name()
                last_name = self.faker.last_name()
                email = f'{first_name.lower()}.{last_name.lower()}{user_id}@example.org'
                age = row[2]
                if age == 'NULL':
                    age = None

                user = User(
                    id=user_id,
                    first_name=first_name,
                    last_name=last_name,
                    password="pbkdf2_sha256$260000$EoTovTO51J1EMhVCgfWM0t$jQjs11u15ELqQDNthGsC+vdLoDJRn2LDjU2qE7KqKj0=",
                    location=row[1],
                    age=age,
                    public_bio=self.faker.text(max_nb_chars=512),
                    email=email,
                    is_email_verified = True
                )

                users.append(user)

                count += 1
                percent_complete = float((count / 278859) * 100)

                print(f'[ DONE: {round(percent_complete)}% | {count}/{self.TOTAL_USERS_IN_DATASET} ]', end='\r')
                if len(users) > 5000:
                    User.objects.bulk_create(users)
                    users = []

            if users:
                User.objects.bulk_create(users)
            print("The users have been successfully seeded")
            print()

    def default_superuser(self):
        User.objects.create_superuser(
            first_name="Ctrl",
            last_name="Intelligence",
            email="ctrl@intelligence.com",
            password='Password123',
            public_bio="Pop Will Eat Itself! This is the day, this is the hour, this is this!",
            favourite_genre="Science Fiction",
            location="Greater London",
            age=20,
            is_email_verified = True
        )
        print("Default superuser created with details:")
        print("Email: ctrl@intelligence.com")
        print("Password: Password123")
        print()

    def load_books(self):
        count = 0
        file_path_users = "data/BX_Books.csv"

        with open(file_path_users, encoding='latin-1') as book_csv_file:
            data = csv.reader(book_csv_file, delimiter=";")
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
                percent_complete = float((count / 271380) * 100)

                print(f'[ DONE: {round(percent_complete)}% | {count}/{self.TOTAL_BOOKS_IN_DATASET} ]', end='\r')

                if len(books) > 5000:
                    Book.objects.bulk_create(books)
                    books = []

            if books:
                Book.objects.bulk_create(books)
            print("The books have been successfully seeded")
            print()

    def load_ratings(self):
        count = 0
        file_path_users = "data/BX-Book-Ratings.csv"

        with open(file_path_users, encoding='latin-1') as rating_csv_file:
            data = csv.reader(rating_csv_file, delimiter=";")
            next(data)
            ratings = []
            for row in data:
                user_getter = int(row[0])
                user = User.objects.filter(id=user_getter).get()

                if not user:
                    user = None

                rating = Rating(
                    user=user,
                    isbn=row[1],
                    rating=int(row[2])
                )

                ratings.append(rating)
                count += 1
                percent_complete = float((count / 1149780) * 100)

                print(f'[ DONE: {round(percent_complete)}% | {count}/{1149780} ]', end='\r')

                if len(ratings) > 5000:
                    Rating.objects.bulk_create(ratings)
                    ratings = []

            if ratings:
                Rating.objects.bulk_create(ratings)
            print("The ratings have been successfully seeded")
            print()
