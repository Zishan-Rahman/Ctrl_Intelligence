from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from bookclub.models import Book, Club


@login_required
def book_list(request):
    books = Book.objects.all()
    memberships = Club.objects.filter(members=request.user) | Club.objects.filter(organisers=request.user) | Club.objects.filter(owner=request.user)
    return render(request, 'book_list.html', {'books': books, "club_memberships": memberships})
