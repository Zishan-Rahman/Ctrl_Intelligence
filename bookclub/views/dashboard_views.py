from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from bookclub.models import Rating
import pandas as pd
from surprise import SVD
from surprise import Dataset, Reader
import pickle




@login_required
def home_page(request):
    return render(request, "home.html", {'user': request.user})


def recommender():
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
        prediction = algo.predict(1000000, str(isbn)).est
        predictions.append([isbn, prediction])

    recommendations = pd.DataFrame(predictions, columns=['isbn', 'rating'])
    print(recommendations.sort_values('rating', ascending=False).head(10))