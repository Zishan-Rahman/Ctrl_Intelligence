"""Books related views."""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
<<<<<<< HEAD
from bookclub.models import Book
from django.views.generic.list import ListView

class BookListView(ListView) :
    @login_required
    def book_list(request):
        books = Book.objects.all()
        return render(request, 'book_list.html', {'books': books})
=======
from django.views.generic import ListView
from bookclub.models import Book, Club

# @login_required
# def book_list(request):
#     books = Book.objects.all()
#     book_paginator = Paginator(books, 10)
#     memberships = Club.objects.filter(members=request.user) | Club.objects.filter(organisers=request.user) | Club.objects.filter(owner=request.user)
#     return render(request, 'book_list.html', {'books': books, "club_memberships": memberships})


class BooksListView(LoginRequiredMixin, ListView):
    """View that shows a list of all books."""

    model = Book
    template_name = "book_list.html"
    context_object_name = "books"
    queryset = Book.objects.all()
    paginate_by = settings.BOOKS_PER_PAGE
>>>>>>> 9a1ba4c6ddf0bed887d962562c16c2893279d1ce
