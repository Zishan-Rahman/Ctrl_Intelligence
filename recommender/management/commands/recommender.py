import sqlite3
from bookclub.models import User, Rating, Club, Book
from surprise import SVD
from surprise import BaselineOnly
from surprise import KNNBasic
from surprise import CoClustering
from surprise import NMF
from surprise import NormalPredictor
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import cross_validate
from surprise.model_selection import train_test_split

import pandas as pd
from collections import defaultdict

from sklearn.neighbors import NearestNeighbors
import numpy as np
from scipy.sparse import csr_matrix

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        processed_df, books = self.pre_process()
        algo = self.recommender_model(processed_df)
        self.get_user_ratings(algo, processed_df, books)

    def pre_process(self):
        books = pd.read_csv('data/BX_Books.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
        users = pd.read_csv('data/BX-Users.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
        book_ratings = pd.read_csv('data/BX-Book-Ratings.csv', sep=';', on_bad_lines='skip', encoding="latin-1")

        users.columns = users.columns.str.strip().str.lower().str.replace('-', '_')
        users.loc[(users.age < 5) | (users.age > 100), 'age'] = np.nan

        user_location_expanded = users.location.str.split(',', 2, expand=True)
        user_location_expanded.columns = ['city', 'state', 'country']
        users = users.join(user_location_expanded)

        users.drop(columns=['location'], inplace=True)

        users.country.replace('', np.nan, inplace=True)

        books.columns = books.columns.str.strip().str.lower().str.replace('-', '_')
        books.drop(columns=['image_url_s', 'image_url_m', 'image_url_l'], inplace=True)

        books.year_of_publication = pd.to_numeric(books.year_of_publication, errors='coerce')

        books.year_of_publication.replace(0, np.nan, inplace=True)

        historical_books = books[books.year_of_publication < 1900]
        books_from_the_future = books[books.year_of_publication > 2018]

        books = books.loc[~(books.isbn.isin(historical_books.isbn))]
        books = books.loc[~(books.isbn.isin(books_from_the_future.isbn))]

        book_ratings.columns = book_ratings.columns.str.strip().str.lower().str.replace('-', '_')

        book_ratings = book_ratings[book_ratings.book_rating != 0]

        books_with_ratings = book_ratings.join(books.set_index('isbn'), on='isbn')

        books_with_ratings.dropna(subset=['book_title'], inplace=True)

        books_users_ratings = books_with_ratings.join(users.set_index('user_id'), on='user_id')

        user_item_rating = books_users_ratings[['user_id', 'isbn', 'book_rating']]

        return user_item_rating, books


    def recommender_model(self, user_item_rating):

        reader = Reader(rating_scale=(1, 10))

        data = Dataset.load_from_df(user_item_rating, reader)

        trainset = data.build_full_trainset()
        algo = NMF()

        recommender = algo.fit(trainset)

        return recommender

        # train_set, test_set = train_test_split(data, test_size=0.2)

        # algo = SVD()
        # algo.fit(train_set)
        # pred = fit.test(test_set)
        # accuracy.rmse(pred)

        # algo = NMF()
        # fit = algo.fit(train_set)
        # pred = fit.test(test_set)
        # accuracy.rmse(pred)

        # algo = KNNBaseline()
        # fit = algo.fit(train_set)
        # pred = fit.test(test_set)
        # accuracy.rmse(pred)

        # algo = KNNWithMeans()
        # fit = algo.fit(train_set)
        # pred = fit.test(test_set)
        # accuracy.rmse(pred)

        # algo = KNNWithZScore()
        # fit = algo.fit(train_set)
        # pred = fit.test(test_set)
        # accuracy.rmse(pred)

        """
        recommend = algo.trainset

        books_list = list(set(user_item_rating['isbn'].to_list()))
        user_item_rating['user_id'].unique()

        predicted_books = []
        for item_id in books_list:
            try:
                if recommend.knows_item(recommend.to_inner_iid(item_id)):
                    predicted_books.append(item_id)
            except:
                pass

        pickle.dump(algo, open("algo.pkl", "wb"))
        books.to_pickle("books.pkl")
        with open('predicted_books.pkl', 'wb') as f:
            pickle.dump(predicted_books, f)
        """

    def get_user_ratings(self, algo, user_item_rating, books):
        user_ratings_df = pd.DataFrame(list(Rating.objects.all().values("user_id", "isbn", "rating")))

        reader = Reader(rating_scale=(1, 10))

        user_ratings_dataset = Dataset.load_from_df(user_ratings_df[['user_id', 'isbn', 'rating']], reader)

        [user_ratings_dataset.df.loc[i].to_list() for i in range(len(user_ratings_dataset.df))]

        book_list = list(set(user_item_rating['isbn'].to_list()))

        iid = '0451526341'
        uid = 503

        print(algo.predict(uid, iid))

        predictions = []
        for isbn in book_list:
            prediction = algo.predict('502', isbn).est
            predictions.append([isbn, prediction])

        recommender = pd.DataFrame(predictions, columns=['isbn', 'rating'])
        merge = pd.merge(recommender, books, on='isbn')
        print(merge.sort_values('rating', ascending=False).head(10))

