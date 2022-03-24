"""Views for recently registered users to be prompted to rate books"""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from bookclub.models import Book, Rating, User
from django.views.generic.edit import View
from django.contrib import messages

@login_required
def introductory_view(request):
    if request.user.get_number_of_ratings() < 10:
        return render(request, 'not_rated_enough_albums.html')
    return redirect('home')
