from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from bookclub.models import Book


@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})
