from django.shortcuts import render
from bookclub.templates import *

# Create your views here.

def landing_page(request):
    return render(request, 'landing_page.html')

def home_page(request):
    return render(request, 'home_page.html')

def user_list(request):
    return render(request, 'user_list.html')

def club_list(request):
    return render(request, 'club_list.html')


