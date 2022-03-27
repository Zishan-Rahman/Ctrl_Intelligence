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

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to book_list if book_id invalid."""
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('book_list')


@login_required
def current_reads(request, user_id):
    user = User.objects.get(id=user_id)
    books = user.currently_reading_books.all()
    return render(request, "reading_list.html", {'books': books, 'user': user})


def add_to_current_reads(request, book_id):
    user = User.objects.get(pk=request.user.id)
    book = Book.objects.get(pk=book_id)
    user.currently_reading_books.add(book)
    messages.add_message(request, messages.SUCCESS, f"{book.title} was successfully added to your reading list!")


def add_to_current_reads_book_list(request, book_id):
    add_to_current_reads(request, book_id)
    return redirect("book_list")


def add_to_current_reads_book_profile(request, book_id):
    add_to_current_reads(request, book_id)
    return redirect("book_profile", book_id=book_id)


def remove_from_current_reads(request, book_id):
    user = User.objects.get(pk=request.user.id)
    book = Book.objects.get(pk=book_id)
    user.currently_reading_books.remove(book)
    messages.add_message(request, messages.ERROR, f"{book.title} was successfully removed from your reading list!")


def remove_from_current_reads_book_list(request, book_id):
    remove_from_current_reads(request, book_id)
    return redirect("book_list")


def remove_from_current_reads_book_profile(request, book_id):
    remove_from_current_reads(request, book_id)
    return redirect("book_profile", book_id=book_id)


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
    Rating.objects.create(user=user, book=book, isbn=isbn, rating=request.POST.get('ratings', "0"))
    messages.add_message(request, messages.SUCCESS,
                         "You have given " + book.title + " a rating of " + request.POST.get('ratings', "0"))
    return redirect('book_profile', book_id=book_id)


def make_favourite(request, book_id):
    user = User.objects.get(pk=request.user.id)
    book = Book.objects.get(pk=book_id)
    user.favourite_books.add(book)
    messages.add_message(request, messages.SUCCESS, book.title + " has been added to Favourites!")


def make_favourite_book_list(request, book_id):
    make_favourite(request, book_id)
    return redirect('book_list')


def make_favourite_book_profile(request, book_id):
    make_favourite(request, book_id)
    return redirect('book_profile', book_id=book_id)


def unfavourite(request, book_id):
    user = User.objects.get(pk=request.user.id)
    book = Book.objects.get(pk=book_id)
    user.favourite_books.remove(book)
    messages.add_message(request, messages.ERROR, book.title + " has been removed from Favourites!")
    return redirect('book_profile', book_id=book_id)


def unfavourite_book_list(request, book_id):
    unfavourite(request, book_id)
    return redirect('book_list')


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
