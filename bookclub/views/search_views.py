import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render
from bookclub.models import Club, Book, User
from django.views.generic.list import ListView
from django.conf import settings

# @login_required
# def search(request):
#     if request.method == "GET":
#         searched = request.GET.get('searched', None)
#         if searched:
#             books = Book.objects.filter(title__contains=searched)
#             return render(request, "home.html", {'searched': searched, 'books': books})
#         else:
#             return render(request, "search_page.html", {})
#
@login_required
def search(request):
	if request.method == "POST":
		query = request.POST['query']
		books = Book.objects.filter(title__contains=query) | Book.objects.filter(isbn__contains=query) | Book.objects.filter(author__contains=query) | Book.objects.filter(author__contains=query) | Book.objects.filter(pub_year__contains=query) | Book.objects.filter(publisher__contains=query)
		clubs = Club.objects.filter(name__contains=query) | Club.objects.filter(description__contains=query) | Club.objects.filter(location__contains=query)
		users = User.objects.filter(first_name__contains=query) | User.objects.filter(last_name__contains=query) | User.objects.filter(public_bio__contains=query) | User.objects.filter(location__contains=query)
		return render(request,
		'search_page.html',
		{'query':query,
		'books':books, 'clubs':clubs, 'users':users})
	else:
		return render(request,
		'search_page.html',
		{})
