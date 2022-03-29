"""Books related views."""
from mimetypes import init
from urllib import request
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.list import MultipleObjectMixin
from bookclub.models import Book, Club, User, Rating
from django.contrib import messages


class BooksListView(LoginRequiredMixin, ListView):
    """View that shows a list of all books."""

    model = Book
    template_name = "book_list.html"
    context_object_name = "books"
    queryset = Book.objects.all()
    paginate_by = settings.BOOKS_PER_PAGE


class ShowBookView(LoginRequiredMixin, DetailView, MultipleObjectMixin):
    """View that shows individual books details."""

    model = Book
    template_name = 'book_profile.html'
    paginate_by = settings.BOOKS_PER_PAGE
    pk_url_kwarg = 'book_id'
    object_list = "books"

    def get_context_data(self, **kwargs):
        context = super(ShowBookView, self).get_context_data(**kwargs)
        book = Book.objects.get(pk=self.kwargs['book_id'])

        if Rating.objects.filter(book=book, user=self.request.user).exists():
            rating = Rating.objects.get(book=book, user=self.request.user)
            context['rating'] = rating.rating
        else:
            rating = 0
            context['rating'] = rating

        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to book_list if book_id invalid."""
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('book_list')


class ReadingListView(LoginRequiredMixin, ListView):

    model = User
    template_name = 'reading_list.html'
    paginate_by = settings.BOOKS_PER_PAGE
    pk_url_kwarg = 'user_id'
    object_list = "books"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        books = user.currently_reading_books.all()
        context['books'] = books

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        books = user.currently_reading_books.all()
        paginator = Paginator(books, settings.BOOKS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'reading_list.html', {"books": books, "user": user, "page_obj": page_obj})

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        books = user.currently_reading_books.all()
        paginator = Paginator(books, settings.BOOKS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'reading_list.html', {"books": books, "user": user, "page_obj": page_obj})

@login_required
def add_to_reading_list(request, book_id):
    user = User.objects.get(pk=request.user.id)
    book = Book.objects.get(pk=book_id)
    user.currently_reading_books.add(book)
    messages.add_message(request, messages.SUCCESS, f"{book.title} was successfully added to your reading list!")

@login_required
def add_to_reading_list_book_list(request, book_id):
    add_to_reading_list(request, book_id)
    return redirect("book_list")

@login_required
def add_to_reading_list_book_profile(request, book_id):
    add_to_reading_list(request, book_id)
    return redirect("book_profile", book_id=book_id)

@login_required
def remove_from_reading_list(request, book_id):
    user = User.objects.get(pk=request.user.id)
    book = Book.objects.get(pk=book_id)
    user.currently_reading_books.remove(book)
    messages.add_message(request, messages.ERROR, f"{book.title} was successfully removed from your reading list!")

@login_required
def remove_from_reading_list_book_list(request, book_id):
    remove_from_reading_list(request, book_id)
    return redirect("book_list")

@login_required
def remove_from_reading_list_book_profile(request, book_id):
    remove_from_reading_list(request, book_id)
    return redirect("book_profile", book_id=book_id)

@login_required
def remove_from_reading_list_page(request, book_id):
    user_id = request.user.id
    remove_from_reading_list(request, book_id)
    return redirect("reading_list", user_id=user_id)


class Favourites(LoginRequiredMixin, ListView):
    model = Book
    template_name = "favourites.html"
    context_object_name = "books"
    paginate_by = settings.BOOKS_PER_PAGE

    def get_queryset(self):
        return self.request.user.favourite_books.all()


def update_ratings(request, book_id):
    user = User.objects.get(pk=request.user.id)
    book = Book.objects.get(pk=book_id)
    isbn = Book.objects.get(pk=book_id).isbn
    if Rating.objects.filter(book=book, user=user).exists():
        Rating.objects.get(book=book, user=user).delete()

    Rating.objects.create(user=user, book=book, isbn=isbn, rating=request.POST.get('ratings', "0"))
    messages.add_message(request, messages.SUCCESS,
                         "You have given " + book.title + " a rating of " + request.POST.get('ratings', "0"))
    return redirect('book_profile', book_id=book_id)

@login_required
def make_favourite(request, book_id):
    user = User.objects.get(pk=request.user.id)
    book = Book.objects.get(pk=book_id)
    user.favourite_books.add(book)
    messages.add_message(request, messages.SUCCESS, book.title + " has been added to Favourites!")

@login_required
def make_favourite_book_list(request, book_id):
    make_favourite(request, book_id)
    return redirect('book_list')

@login_required
def make_favourite_book_profile(request, book_id):
    make_favourite(request, book_id)
    return redirect('book_profile', book_id=book_id)

@login_required
def unfavourite(request, book_id):
    user = User.objects.get(pk=request.user.id)
    book = Book.objects.get(pk=book_id)
    user.favourite_books.remove(book)
    messages.add_message(request, messages.ERROR, book.title + " has been removed from Favourites!")
    return redirect('book_profile', book_id=book_id)

@login_required
def unfavourite_book_list(request, book_id):
    unfavourite(request, book_id)
    return redirect('book_list')

@login_required
def unfavourite_book_profile(request, book_id):
    unfavourite(request, book_id)
    return redirect('book_profile', book_id=book_id)


class MyBookRatings(LoginRequiredMixin, ListView):
    model = Rating
    template_name = "my_book_ratings.html"
    context_object_name = "ratings"
    paginate_by = settings.BOOKS_PER_PAGE

    def get(self, request):
        """Display application template"""
        return self.render()

    def render(self):
        user = User.objects.get(pk=self.request.user.id)
        ratings = Rating.objects.filter(user=user)

        paginator = Paginator(ratings, settings.APPLICATIONS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(self.request, 'my_book_ratings.html', {'ratings': ratings, 'page_obj': page_obj})
