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


@login_required
def book_profile(request, book_id):
    """ Individual Book's Profile Page """
    book = Book.objects.get(id = book_id)
    current_user = request.user
    return render(request, 'book_profile.html',{'current_user':current_user})


class ShowBookView(LoginRequiredMixin, DetailView, MultipleObjectMixin):
    """View that shows individual books details."""

    model = Book
    template_name = 'book_profile.html'
    paginate_by = settings.BOOKS_PER_PAGE
    pk_url_kwarg = 'book_id'
    object_list = "books"

    # def get_context_data(self, **kwargs):
    #     """Generate context data to be shown in the template."""
    #     user = self.get_object()
    #     context = super().get_context_data( **kwargs)
    #     context['user'] = user
    #     return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to user_list if user_id invalid."""

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('book_list')
