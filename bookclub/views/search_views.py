import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.shortcuts import render
from bookclub.models import Club, Book, User
from django.views.generic.list import ListView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Value as V
from django.db.models.functions import Concat



@login_required
def search(request):
    if request.method == "POST":
        query = request.POST['query']
        books = Book.objects.filter(title__icontains=query) | Book.objects.filter(isbn__icontains=query) | Book.objects.filter(author__icontains=query) | Book.objects.filter(pub_year__icontains=query) | Book.objects.filter(publisher__icontains=query)
        clubs = Club.objects.filter(name__icontains=query)
        users = User.objects.annotate(full_name=Concat('first_name', V(' '), 'last_name')).filter(full_name__icontains=query) | User.objects.filter(email__icontains=query)
        return render(request, 'search_page.html', {'query': query, 'books': books[:10], 'clubs': clubs[:10], 'users': users[:10]})
    else:
        return render(request, 'search_page.html', {})


def search_autocomplete(request):
    if 'term' in request.GET:
        query = Book.objects.filter(title__icontains=request.GET.get('term'))[:5]
        books = list()
        for book in query:
            books.append(book.title)
        return JsonResponse(books, safe=False)
