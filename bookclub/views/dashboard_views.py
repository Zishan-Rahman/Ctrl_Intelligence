from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from bookclub.models import Club
from django.db.models.query import QuerySet

@login_required
def home_page(request):
    memberships = Club.objects.filter(members=request.user) | Club.objects.filter(organisers=request.user) | Club.objects.filter(owner=request.user)
    return render(request, "home.html", {"club_memberships": memberships})
