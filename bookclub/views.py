from django.shortcuts import render
from bookclub.templates import *

# Create your views here.

def landing_page(request):
    return render(request, 'landing_page.html')
