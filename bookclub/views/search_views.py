import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render
from bookclub.models import Club, Book
from django.views.generic.list import ListView

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

def search_books(request):
	if request.method == "POST":
		query = request.POST['query']
		books = Book.objects.filter(title__contains=query) | Book.objects.filter(isbn__contains=query) | Book.objects.filter(author__contains=query) | Book.objects.filter(author__contains=query) | Book.objects.filter(pub_year__contains=query) | Book.objects.filter(publisher__contains=query)
		return render(request,
		'search_page.html',
		{'query':query,
		'books':books})
	else:
		return render(request,
		'search_page.html',
		{})
