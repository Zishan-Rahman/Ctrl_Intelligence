import pickle
import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand, CommandError
from surprise.accuracy import rmse
from surprise import accuracy
from surprise import SVD, KNNBasic, KNNBaseline, KNNWithZScore, KNNWithMeans, BaselineOnly, NMF, CoClustering, \
    NormalPredictor, SlopeOne
from surprise.model_selection import cross_validate
from surprise import Dataset, Reader


def evaluator():
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

    books_list = ratings.isbn.value_counts().rename_axis('isbn').reset_index(name='count')
    books_list = books_list[books_list['count'] > 5]['isbn'].to_list()

    users_list = ratings.user_id.value_counts().rename_axis('user_id').reset_index(name='count')
    users_list = users_list[users_list['count'] > 5]['user_id'].to_list()

    ratings = ratings[ratings['isbn'].isin(books_list)]
    ratings = ratings[ratings['user_id'].isin(users_list)]

    books_with_ratings = ratings.join(books.set_index('isbn'), on='isbn')

    books_with_ratings.dropna(subset=['book_title'], inplace=True)

    books_users_ratings = books_with_ratings.join(users.set_index('user_id'), on='user_id')

    user_rating_df = books_users_ratings[['user_id', 'isbn', 'book_rating']]

    reader = Reader(rating_scale=(1, 10))

    data = Dataset.load_from_df(user_rating_df[['user_id', 'isbn', 'book_rating']], reader)

    print('SVD', cross_validate(SVD(), data, measures=['RMSE'], cv=5, verbose=True))
    print('KNNBaseline', cross_validate(KNNBaseline(), data, measures=['RMSE'], cv=5, verbose=True))
    print('KNNBasic', cross_validate(KNNBasic(), data, measures=['RMSE'], cv=5, verbose=True))
    print('KNNWithMeans', cross_validate(KNNWithMeans(), data, measures=['RMSE'], cv=5, verbose=True))
    print('KNNWithZScore', cross_validate(KNNWithZScore(), data, measures=['RMSE'], cv=5, verbose=True))
    print('BaselineOnly', cross_validate(BaselineOnly(), data, measures=['RMSE'], cv=5, verbose=True))
    print('NMF', cross_validate(NMF(), data, measures=['RMSE'], cv=5, verbose=True))
    print('CoClustering', cross_validate(CoClustering(), data, measures=['RMSE'], cv=5, verbose=True))
    print('NormalPredictor', cross_validate(NormalPredictor(), data, measures=['RMSE'], cv=5, verbose=True))
    print('SlopeOne', cross_validate(SlopeOne(), data, measures=['RMSE'], cv=5, verbose=True))


class Command(BaseCommand):

    def handle(self, *args, **options):
        evaluator()
