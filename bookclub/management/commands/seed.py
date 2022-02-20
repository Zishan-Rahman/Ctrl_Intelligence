import random
from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from bookclub.models import User, Club, Book
from django.core.exceptions import ValidationError
import csv


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


def create_set_clubs():
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
    for i in range(0, 50):
        random_user = random.choice(users)
        all_clubs_users = get_all_clubs_users(club)
        if random_user not in all_clubs_users:
            club.make_member(random_user)

    for i in range(0, 20):
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
            print('NORMAL')
            print()
            create_set_users()
            print('Created set users')
            print()
            self.default_superuser()
            print()
            print('Seed users:')
            print()
            self.generate_users()
            print('Users successfully seeded')
            print()
            print('Seed clubs:')
            print()
            create_set_clubs()
            print('Created set clubs')
            print()
            self.generate_clubs()
            print('Clubs successfully seeded')
            print()
            self.generate_limited_books_dataset()
            print("Books (smaller dataset) successfully seeded")
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
        User.objects.create_superuser(email="ctrl@intelligence.com", password='Password123')
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
                percent_complete = float((total_users/self.TOTAL_USERS)*100)
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
                total_clubs = get_total_clubs()
                percent_complete = float((total_clubs / self.TOTAL_CLUBS) * 100)
                print(f'[ DONE: {round(percent_complete)}% | {total_clubs}/{self.TOTAL_CLUBS} ]', end='\r')
            except ValidationError:
                pass

    def generate_limited_books_dataset(self):
        count = 0
        file_path_users = "data/BX_Books.csv"

        with open(file_path_users, encoding='cp1252') as book_csv_file:
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
                percent_complete = float((count/5000)*100)

                print(f'[ DONE: {round(percent_complete)}% | {count}/{5000} ]', end='\r')

                if len(books) > 5000:
                    break

            if books:
                Book.objects.bulk_create(books)
