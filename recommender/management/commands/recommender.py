from bookclub.models import User, Rating, Club, Book
from surprise import SVD
from surprise import BaselineOnly
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


def pre_process():
    """ Load dataset and clean data """

    books = pd.read_csv('data/BX_Books.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
    users = pd.read_csv('data/BX-Users.csv', sep=';', on_bad_lines='skip', encoding="latin-1")
    ratings = pd.read_csv('data/BX-Book-Ratings.csv', sep=';', on_bad_lines='skip', encoding="latin-1")

    users.columns = users.columns.str.strip().str.lower().str.replace('-', '_')

    books.columns = books.columns.str.strip().str.lower().str.replace('-', '_')
    books.drop(columns=['image_url_s', 'image_url_m', 'image_url_l'], inplace=True)

    ratings.columns = ratings.columns.str.strip().str.lower().str.replace('-', '_')

    books = books[books.year_of_publication != 0]
    books = books[books.year_of_publication != np.nan]

    book_dates_too_old = books[books.year_of_publication < 1800]
    book_dates_future = books[books.year_of_publication > 2022]

    books = books.loc[~(books.isbn.isin(book_dates_too_old.isbn))]
    books = books.loc[~(books.isbn.isin(book_dates_future.isbn))]

    ratings = ratings[ratings.book_rating != 0]

    books_list = ratings.isbn.value_counts().rename_axis('isbn').reset_index(name='count')
    books_list = books_list[books_list['count'] > 10]['isbn'].to_list()

    users_list = ratings.user_id.value_counts().rename_axis('user_id').reset_index(name='count')
    users_list = users_list[users_list['count'] > 10]['user_id'].to_list()

    ratings = ratings[ratings['isbn'].isin(books_list)]
    ratings = ratings[ratings['user_id'].isin(users_list)]

    books_with_ratings = ratings.join(books.set_index('isbn'), on='isbn')

    books_with_ratings.dropna(subset=['book_title'], inplace=True)

    books_users_ratings = books_with_ratings.join(users.set_index('user_id'), on='user_id')

    user_item_rating = books_users_ratings[['user_id', 'isbn', 'book_rating']]

    return user_item_rating, books


def recommender_model(user_item_rating):

    reader = Reader(rating_scale=(1, 10))

    data = Dataset.load_from_df(user_item_rating, reader)

    trainset = data.build_full_trainset()
    algo = NMF()

    algo.fit(trainset)

    return algo

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


def get_user_ratings(algo, books):
    user_ratings_df = pd.DataFrame(list(Rating.objects.all().values("user_id", "isbn", "rating")))

    #print(user_ratings_df.head())

    reader = Reader(rating_scale=(1, 10))

    user_ratings_dataset = Dataset.load_from_df(user_ratings_df[['user_id', 'isbn', 'rating']], reader)

    #valid_df = pd.DataFrame({'user_id': [1000502, 1000502, 1000502, 1000502, 1000502, 1000502, 1000502, 1000502,
    #                                     1000502, 1000502, 1000502, 1000502, 1000502, 1000502, 1000502],
    #                         'isbn': ['0060504072', '0060921145', '0060959037', '037575931X', '0385496095',
    #                                  '039302749X', '0446310786', '044990928X', '0670894605', '0671026372',
    #                                  '0671793888', '067943299X', '0679442405', '0743226631', '0843141786'],
    #                         'rating': [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]})

    # valid_df_1 = pd.DataFrame({'user_id': [1000501, 1000501, 1000501, 1000501, 1000501, 1000501, 1000501, 1000501, 1000501, 1000501, 1000501, 1000501, 1000501, 1000501, 1000501],
    #                        'isbn': ['0060504072', '0060921145', '0060959037', '037575931X', '0385496095',
    #                                  '039302749X', '0446310786', '044990928X', '0670894605', '0671026372',
    #                                  '0671793888', '067943299X', '0679442405', '0743226631', '0843141786'],
    #                         'rating': [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]})

    # frames = [valid_df, valid_df_1, user_ratings_df, user_item_rating]

    # result = pd.concat(frames, ignore_index=True)

    #valid_Dataset = Dataset.load_from_df(valid_df[['user_id', 'isbn', 'rating']], reader)

    # sqr_1 = [valid_Dataset.df.loc[i].to_list() for i in range(len(valid_Dataset.df))]

    # print(sqr_1)

    sqr = [user_ratings_dataset.df.loc[i].to_list() for i in range(len(user_ratings_dataset.df))]

    #sqr_2 = [valid_Dataset.df.loc[i].to_list() for i in range(len(valid_Dataset.df))]

    def get_top_n(predictions, n=10):
        '''Return the top-N recommendation for each user from a set of predictions.

        Args:
            predictions(list of Prediction objects): The list of predictions, as
                returned by the test method of an algorithm.
            n(int): The number of recommendation to output for each user. Default
                is 10.

        Returns:
        A dict where keys are user (raw) ids and values are lists of tuples:
            [(raw item id, rating estimation), ...] of size n.
        '''

        # First map the predictions to each user.
        top_n = defaultdict(list)
        for uid, iid, true_r, est, _ in predictions:
            top_n[uid].append((iid, est))

        # Then sort the predictions for each user and retrieve the k highest ones.
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]

        return top_n

    pred = algo.test(sqr)

    def get_reading_list(userid):
        """
        Retrieve full book titles from full 'books_users_ratings' dataframe
        """
        reading_list = defaultdict(list)
        top_n = get_top_n(pred, n=10)
        for book in top_n[userid]:
            title = books.loc[books.isbn == book].book_title.unique()[0]
            isbn = books.loc[books.isbn == book].isbn.unique()[0]
            reading_list[title] = isbn
        return reading_list

    example_reading_list = get_reading_list(userid=1000502)
    for book, isbn in example_reading_list.items():
        print(f'{book}: {isbn}')

    """
    books_list = list(set(user_item_rating['isbn'].to_list()))

    predictions = []
    for isbn in books_list:
        prediction = algo.predict(1000502, str(isbn)).est
        predictions.append([isbn, prediction])

    recom = pd.DataFrame(predictions, columns=['isbn', 'rating'])
    merge = pd.merge(recom, books, on='isbn')

    print(merge.sort_values('rating', ascending=False).head(10))
    """


class Command(BaseCommand):

    def handle(self, *args, **options):
        processed_df, books = pre_process()
        algo = recommender_model(processed_df)
        get_user_ratings(algo, books)

