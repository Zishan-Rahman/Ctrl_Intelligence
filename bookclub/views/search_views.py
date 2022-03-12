import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render
from bookclub.models import Club, Book, User, Application
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

@login_required
def applications_search(request):
	if request.method == "POST":
		query = request.POST['query']
		current_user = request.user
		applicants = []
		application = []
		owned_clubs = Club.objects.filter(owner=current_user)
		for a in Application.objects.all():
			if a.club in owned_clubs:
				applicants.append(a)

		users = User.objects.annotate(full_name=Concat('first_name', V(' '), 'last_name')).filter(full_name__icontains=query)
		clubs = Club.objects.filter(name__contains=query)
		for i in applicants:
			if i.applicant in users:
				application.append(i)
			if i.club in clubs:
				application.append(i)

		#prevents duplications being printed
		application = list(dict.fromkeys(application))

        # paginator = Paginator(applicants, settings.APPLICATIONS_PER_PAGE)
        # page_number = self.request.GET.get('page')
        # page_obj = paginator.get_page(page_number)
		return render(request, 'applications_search.html', {'query': query, 'application': application})
	else:
		return render(request, 'applications_search.html', {})
