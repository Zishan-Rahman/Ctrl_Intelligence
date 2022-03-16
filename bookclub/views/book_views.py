"""Books related views."""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.list import MultipleObjectMixin
from bookclub.models import Book, Club, User

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
def current_reads(request):
    user = User.objects.get(id = request.user.id)
    books = user.currently_reading_books.all()
    return render(request, "current_reads.html", {'books':books})

def add_to_current_reads(request, book_id):
    user = User.objects.get(id = request.user.id)
    book = Book.objects.get(id=book_id)
    user.currently_reading_books.add(book)
    user.save()
    return render(request, "home.html")

@login_required
def books_read(request):
    user = User.objects.get(id = request.user.id)
    books = user.already_read_books.all()
    return render(request, "books_read.html", {'books':books})

def add_to_books_read(request, book_id):
    user = User.objects.get(id = request.user.id)
    book = Book.objects.get(id=book_id)
    user.already_read_books.add(book)
    user.save()
    return render(request, "home.html")
