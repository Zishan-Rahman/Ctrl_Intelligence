import random
from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from bookclub.models import User, Club, Book, Application, Post, UserPost
from django.core.exceptions import ValidationError
import csv
import pandas as pd
import numpy as np


def create_set_users():
    User.objects.create(
        pk=1000000,
        first_name="John",
        last_name="Doe",
        email="johndoe@bookclub.com",
        public_bio="I'm just an abstract concept!",
        favourite_genre="Science fiction",
        location="London",
        age=39,
        password="pbkdf2_sha256$260000$EoTovTO51J1EMhVCgfWM0t$jQjs11u15ELqQDNthGsC+vdLoDJRn2LDjU2qE7KqKj0=",
        is_email_verified=True
    )
    User.objects.create(
        first_name="Jane",
        last_name="Doe",
        email="janedoe@bookclub.com",
        public_bio="I'm also an abstract concept!",
        favourite_genre="Adventure",
        location="Oxford",
        age=32,
        password="pbkdf2_sha256$260000$EoTovTO51J1EMhVCgfWM0t$jQjs11u15ELqQDNthGsC+vdLoDJRn2LDjU2qE7KqKj0=",
        is_email_verified=True
    )
    User.objects.create(
        first_name="Joe",
        last_name="Doe",
        email="joedoe@bookclub.com",
        public_bio="Just another fake user again!",
        favourite_genre="Romance",
        location="London",
        age=52,
        password="pbkdf2_sha256$260000$EoTovTO51J1EMhVCgfWM0t$jQjs11u15ELqQDNthGsC+vdLoDJRn2LDjU2qE7KqKj0=",
        is_email_verified=True
    )


def generate_genre():
    genres = ['Action', 'Adventure', 'Romance', 'Science Fiction', 'Horror', 'Non-fiction', 'Poetry', 'Thriller',
              'Classics', 'Comics', 'Crime', 'Fantasy', 'Psychological', 'Foreign', 'Biographies', 'Religious']
    return random.choice(genres)


def generate_provider():
    providers = ['aol', 'yahoo', 'gmail', 'outlook', 'protonmail', 'hotmail', 'gov', 'icloud']
    return random.choice(providers)


def generate_boolean():
    boolean = [True, False]
    return random.choice(boolean)


def generate_owner():
    return list(User.objects.all())[random.randint(0, User.objects.count() - 1)]


def get_total_users():
    return User.objects.all().count()


def get_total_clubs():
    return Club.objects.all().count()


def get_all_users_list():
    return list(User.objects.all())


def get_all_clubs_users(club):
    return club.get_all_users()


def generate_club_hierarchy(club):
    users = get_all_users_list()
    for i in range(0, 15):
        application_possible = True
        random_user = random.choice(users)
        all_club_users = get_all_clubs_users(club)
        current_applications = Application.objects.filter(applicant=random_user, club=club).count()
        if current_applications or random_user in all_club_users:
            application_possible = False
        if application_possible:
            Application.objects.create(
                applicant=random_user,
                club=club
            )

    for i in range(0, 30):
        random_user = random.choice(users)
        all_clubs_users = get_all_clubs_users(club)
        if random_user not in all_clubs_users:
            club.make_member(random_user)

    for i in range(0, 10):
        random_user = random.choice(users)
        all_clubs_users = get_all_clubs_users(club)
        if random_user not in all_clubs_users:
            club.make_member(random_user)
            club.make_organiser(random_user)


class Command(BaseCommand):
    faker = Faker('en_GB')
    TOTAL_USERS = 500
    TOTAL_CLUBS = 50

    def handle(self, *args, **options):
        seed_possible = self.verify_seeding_possible()
        if seed_possible:
            print()
            print("Seed books:")
            self.load_books()
            print("All books have been successfully seeded")
            print()
            create_set_users()
            print('Created set users')
            print()
            self.default_superuser()
            print()
            print('Seed users:')
            print()
            self.generate_users()
            print('All users have been successfully seeded')
            print()
            print('Seed clubs:')
            print()
            self.create_set_clubs()
            print('Created set clubs')
            print()
            self.generate_clubs()
            print('All clubs have been successfully seeded')
            print()
            print('Seeder has successfully completed')

        else:
            print()
            print('The database must first be unseeded.')
            print('To do this, enter the command below:')
            print('> python3 manage.py unseed')
            print()

    def verify_seeding_possible(self):
        seed_possible = True
        users_present = User.objects.count()
        clubs_present = Club.objects.count()

        if users_present > 0:
            seed_possible = False

        if clubs_present > 0:
            seed_possible = False

        return seed_possible

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
            is_email_verified=True,
        )
        print("Default superuser created with details:")
        print("Email: ctrl@intelligence.com")
        print("Password: Password123")
        print()

    def create_user(self):
        provider = generate_provider()
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = f'{first_name.lower()}.{last_name.lower()}@{provider}.com'
        password = 'pbkdf2_sha256$260000$EoTovTO51J1EMhVCgfWM0t$jQjs11u15ELqQDNthGsC+vdLoDJRn2LDjU2qE7KqKj0='
        bio = self.faker.text(max_nb_chars=400)
        genre = generate_genre()
        location = self.faker.city()
        age = random.randint(16, 100)

        generatedUser = User(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            public_bio=bio,
            favourite_genre=genre,
            location=location,
            age=age)
        return generatedUser

    def create_club(self):
        location = self.faker.city()
        name = location + ' Book Club'
        description = self.faker.text(512)
        owner = generate_owner()
        meeting_online = generate_boolean()

        generatedClub = Club(
            name=name,
            description=description,
            location=location,
            owner=owner,
            meeting_online=meeting_online
        )
        return generatedClub

    def generate_users(self):
        total_users = 0
        while total_users < self.TOTAL_USERS:
            try:
                temp_user = self.create_user()
                temp_user.full_clean()
                temp_user.save()
                total_users = get_total_users()
                percent_complete = float((total_users / self.TOTAL_USERS) * 100)
                print(f'[ DONE: {round(percent_complete)}% | {total_users}/{self.TOTAL_USERS} ]', end='\r')
            except ValidationError:
                pass

    def generate_clubs(self):
        total_clubs = 0
        while total_clubs < self.TOTAL_CLUBS:
            try:
                temp_club = self.create_club()
                temp_club.full_clean()
                temp_club.save()
                generate_club_hierarchy(temp_club)
                self.generate_club_posts(temp_club)
                total_clubs = get_total_clubs()
                percent_complete = float((total_clubs / self.TOTAL_CLUBS) * 100)
                print(f'[ DONE: {round(percent_complete)}% | {total_clubs}/{self.TOTAL_CLUBS} ]', end='\r')
            except ValidationError:
                pass

    def generate_club_posts(self, club):
        number_of_posts = random.randint(0, 25)
        club_owner = club.owner
        for i in range(0, number_of_posts):
            text = self.faker.text(max_nb_chars=120)
            Post.objects.create(club=club, author=club_owner, text=text)

    def create_set_clubs(self):
        owner_john = User.objects.get(email="johndoe@bookclub.com")
        bush_house = Club.objects.create(
            name="Bush House Book Club",
            description="Bush House Official Book Club!",
            location="Strand, London",
            owner=owner_john,
            meeting_online=True
        )
        bush_house.full_clean()
        bush_house.save()
        generate_club_hierarchy(bush_house)
        self.generate_club_posts(bush_house)

        owner_jane = User.objects.get(email="janedoe@bookclub.com")
        somerset_house = Club.objects.create(
            name="Somerset House Book Club",
            description="Somerset House Official Book Club!",
            location="Strand, London",
            owner=owner_jane,
            meeting_online=True
        )
        somerset_house.full_clean()
        somerset_house.save()
        generate_club_hierarchy(somerset_house)
        self.generate_club_posts(somerset_house)

        strand_house = Club.objects.create(
            name="Strand House Book Club",
            description="Strand House Official Book Club!",
            location="Strand, London",
            owner=owner_john,
            meeting_online=False
        )
        strand_house.full_clean()
        strand_house.save()
        generate_club_hierarchy(strand_house)
        self.generate_club_posts(strand_house)

    def load_books(self):
        count = 0

        books = pd.read_csv('data/BX_Books.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
        books.columns = books.columns.str.strip().str.lower().str.replace('-', '_')

        ratings = pd.read_csv('data/BX-Book-Ratings.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
        ratings.columns = ratings.columns.str.strip().str.lower().str.replace('-', '_')

        ratings = ratings[ratings.book_rating != 0]

        books = books[books.year_of_publication != 0]
        books = books[books.year_of_publication != np.nan]
        book_dates_too_old = books[books.year_of_publication < 1800]
        book_dates_future = books[books.year_of_publication > 2022]
        books = books.loc[~(books.isbn.isin(book_dates_too_old.isbn))]
        books = books.loc[~(books.isbn.isin(book_dates_future.isbn))]

        books = books.values.tolist()

        books_list = ratings.isbn.value_counts().rename_axis('isbn').reset_index(name='count')
        books_list = books_list[books_list['count'] > 5]['isbn'].to_list()


        create_books_lists = []

        for book in books:
            if book[0] in books_list:
                book_to_append = Book(
                    isbn=book[0].upper(),
                    title=book[1],
                    author=book[2],
                    pub_year=book[3],
                    publisher=book[4],
                    small_url=book[5],
                    medium_url=book[6],
                    large_url=book[7]
                )
                create_books_lists.append(book_to_append)
                count += 1
                percent_complete = float((count / len(books_list)) * 100)

                print(f'[ DONE: {round(percent_complete)}% | {count}/{len(books_list)} ]', end='\r')

                if len(create_books_lists) > 50:
                    Book.objects.bulk_create(create_books_lists)
                    create_books_lists = []

        if create_books_lists:
            Book.objects.bulk_create(create_books_lists)

