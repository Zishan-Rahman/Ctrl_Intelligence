import pickle
import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand, CommandError


def pre_process():
    """ Load dataset and clean data """

    books = pd.read_csv('data/BX_Books.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
    users = pd.read_csv('data/BX-Users.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
    ratings = pd.read_csv('data/BX-Book-Ratings.csv', sep=';', on_bad_lines='skip', encoding="latin-1")

    users.columns = users.columns.str.strip().str.lower().str.replace('-', '_')

    books.columns = books.columns.str.strip().str.lower().str.replace('-', '_')
    books.drop(columns=['image_url_s', 'image_url_m', 'image_url_l'], inplace=True)

    ratings.columns = ratings.columns.str.strip().str.lower().str.replace('-', '_')

    """ Remove books with a publication year: zero, non-existent, in the future or too old for most readers """

    books = books[books.year_of_publication != 0]
    books = books[books.year_of_publication != np.nan]
    book_dates_too_old = books[books.year_of_publication < 1800]
    book_dates_future = books[books.year_of_publication > 2022]
    books = books.loc[~(books.isbn.isin(book_dates_too_old.isbn))]
    books = books.loc[~(books.isbn.isin(book_dates_future.isbn))]

    """ Remove all implicit ratings """

    ratings = ratings[ratings.book_rating != 0]

    """ Get only books and users whom have more than 10 ratings respectively """

    books_list = ratings.isbn.value_counts().rename_axis('isbn').reset_index(name='count')
    books_list = books_list[books_list['count'] > 10]['isbn'].to_list()

    users_list = ratings.user_id.value_counts().rename_axis('user_id').reset_index(name='count')
    users_list = users_list[users_list['count'] > 10]['user_id'].to_list()

    ratings = ratings[ratings['isbn'].isin(books_list)]
    ratings = ratings[ratings['user_id'].isin(users_list)]

    books_with_ratings = ratings.join(books.set_index('isbn'), on='isbn')

    books_with_ratings.dropna(subset=['book_title'], inplace=True)

    books_users_ratings = books_with_ratings.join(users.set_index('user_id'), on='user_id')

    user_rating_df = books_users_ratings[['user_id', 'isbn', 'book_rating']]

    user_rating_df.rename(columns={'book_rating': 'rating'}, inplace=True)

    """ Return the cleaned ratings dataset as a pickle """

    pickle.dump(user_rating_df, open('data/user_item_rating.p', 'wb'))


class Command(BaseCommand):

    def handle(self, *args, **options):
        pre_process()

