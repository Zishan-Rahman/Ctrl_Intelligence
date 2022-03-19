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
		books = Book.objects.filter(title__contains=query) | Book.objects.filter(isbn__contains=query) | Book.objects.filter(author__contains=query) | Book.objects.filter(pub_year__contains=query) | Book.objects.filter(publisher__contains=query)
		clubs = Club.objects.filter(name__contains=query)
		users = User.objects.annotate(full_name=Concat('first_name', V(' '), 'last_name')).filter(full_name__icontains=query)
		return render(request, 'search_page.html', {'query': query, 'books': books, 'clubs': clubs, 'users': users})
	else:
		return render(request, 'search_page.html', {})


def search_autocomplete(request):
    if 'term' in request.GET:
        query = Book.objects.filter(title__contains=request.GET.get('term'))
        books = list()
        for book in query:
            books.append(book.title)
        return JsonResponse(books, safe=False)
