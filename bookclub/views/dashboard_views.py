import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render
from bookclub.models import Club

@login_required
def home_page(request):
    return render(request, "home.html", {'user': request.user})
