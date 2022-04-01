from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from bookclub.models import Rating, Book, RecommendedBook, Club, Post
import pandas as pd
from surprise import SVD
from surprise import Dataset, Reader
import pickle
from bookclub.views import config
from django.contrib import messages

 
@login_required
def home_page(request):
    config.inbox_count(request)
    posts = get_all_club_posts(request)
    posts = posts[:5]
    popular_books_list = get_popular_books()
    popular_books = get_recommended_books(popular_books_list)
    top_n = 10
    recommendations_list = []
    recommendations_list_isbn = []
    user_ratings_count = Rating.objects.filter(user=request.user).count()
    if user_ratings_count >= 10:
        recommended_books_count = RecommendedBook.objects.filter(user=request.user).count()
        if recommended_books_count > 0:
            recommendations_list = list(set(RecommendedBook.objects.filter(user=request.user)))
            for item in recommendations_list:
                recommendations_list_isbn.append(item.isbn)
            recommended_books = get_recommended_books(recommendations_list_isbn)

        else:
            recommendations_list = recommender(request, request.user.id, top_n)
            recommended_books = get_recommended_books(recommendations_list)
            for item in recommended_books:
                RecommendedBook.objects.create(user=request.user, isbn=item.isbn)
    else:
        recommended_books = []
    return render(request, "home.html",
                  {'user': request.user, 'recommendations': recommended_books, 'popular_books': popular_books[:10],
                   'posts': posts})


def refresh_recommendations(request):
    try:
        RecommendedBook.objects.filter(user=request.user).delete()
    except:
        messages.add_message(request, messages.ERROR, "Unable to get your recommendations.")
    return redirect('home')


def club_util(request):
    user_clubs_list = []
    clubs = Club.objects.all()

    for temp_club in clubs:
        if request.user in temp_club.get_all_users():
            user_clubs_list.append(temp_club)

    config.user_clubs = user_clubs_list


def get_all_club_posts(request):
    club_util(request)
    all_club_posts = []

    for club in config.user_clubs:
        club_posts = list(set(Post.objects.filter(club=club)))
        if club_posts:
            for post in club_posts:
                all_club_posts.append(post)
    all_club_posts.sort(key=lambda p: p.created_at, reverse=True)
    return all_club_posts


def get_recommended_books(recommendations_list):
    recommended_books = []
    for book in recommendations_list:
        rec_book = Book.objects.filter(isbn=book)
        if rec_book:
            book_item = rec_book.get()
            recommended_books.append(book_item)
    return recommended_books


def get_popular_books():
    most_popular_item_df = pickle.load(open("data/most_popular_item.p", 'rb'))
    most_popular_list = list(set(most_popular_item_df['isbn'].to_list()))
    return most_popular_list


def recommender(request, user_id, top_n):
    user_rating_df = pickle.load(open("data/user_item_rating.p", "rb"))
    new_ratings_df = pd.DataFrame(list(Rating.objects.all().values("user_id", "isbn", "rating")))

    user_already_rated = Rating.objects.filter(user=request.user)

    user_already_rated_isbn = []

    for item in user_already_rated:
        user_already_rated_isbn.append(item.isbn)

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
        if isbn not in user_already_rated_isbn:
            prediction = algo.predict(user_id, str(isbn)).est
            predictions.append([isbn, prediction])

    recommendations = pd.DataFrame(predictions, columns=['isbn', 'rating'])
    top_n_recommendations = recommendations.sort_values('rating', ascending=False).head(top_n)
    isbn_list = list(set(top_n_recommendations['isbn'].to_list()))

    return isbn_list
