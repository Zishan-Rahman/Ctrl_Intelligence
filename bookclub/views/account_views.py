from django.shortcuts import render
from bookclub.templates import *
from django.contrib.auth.decorators import login_required

# Create your views here.

def landing_page(request):
    return render(request, 'landing_page.html')

@login_required
def home_page(request):
    return render(request, 'home_page.html')

@login_required
def user_list(request):
    return render(request, 'user_list.html')

@login_required
def club_list(request):
    return render(request, 'club_list.html')
