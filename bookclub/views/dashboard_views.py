from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from bookclub.models import Rating, Book
import pandas as pd
from surprise import SVD
from surprise import Dataset, Reader
import pickle

RECOMMENDATIONS_LIST_GLB = []
TOP_N = 10

@login_required
def home_page(request):
    if len(RECOMMENDATIONS_LIST_GLB) > 0:
        recommended_books = get_recommended_books(RECOMMENDATIONS_LIST_GLB)
        return render(request, "home.html", {'user': request.user, 'recommendations': recommended_books})
    else:
        recommendations_list = recommender(request.user.id, TOP_N)
        recommended_books = get_recommended_books(recommendations_list)

    return render(request, "home.html", {'user': request.user, 'recommendations': recommended_books})


def get_recommended_books(recommendations_list):
    recommended_books = []
    for book in recommendations_list:
        rec_book = Book.objects.filter(isbn=book)
        if rec_book:
            rec_book.get()
            recommended_books.append(rec_book)
    return recommended_books


def recommender(user_id, top_n):
    user_rating_df = pickle.load(open("data/user_item_rating.p", "rb"))
    new_ratings_df = pd.DataFrame(list(Rating.objects.all().values("user_id", "isbn", "rating")))
    reader = Reader(rating_scale=(1, 10))
    frames = [new_ratings_df, user_rating_df]
    result = pd.concat(frames, ignore_index=True)
    data = Dataset.load_from_df(result[['user_id', 'isbn', 'rating']], reader)

    trainset = data.build_full_trainset()
    algo = SVD()
    algo.fit(trainset)

    books_list = list(set(user_rating_df['isbn'].to_list()))

    """Adapted from Kaggle.com"""

    predictions = []
    for isbn in books_list:
        prediction = algo.predict(user_id, str(isbn)).est
        predictions.append([isbn, prediction])

    recommendations = pd.DataFrame(predictions, columns=['isbn', 'rating'])
    top_n_recommendations = recommendations.sort_values('rating', ascending=False).head(top_n)
    isbn_list = list(set(top_n_recommendations['isbn'].to_list()))
    global RECOMMENDATIONS_LIST_GLB
    RECOMMENDATIONS_LIST_GLB = isbn_list
    return isbn_list


