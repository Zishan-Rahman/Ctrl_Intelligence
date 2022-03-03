"""Clubs related views."""
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import ListView
from bookclub.forms import ClubForm
from bookclub.models import Club
from bookclub.views import config
from django.urls import reverse

def club_util(request):
    user_clubs_list = []
    clubs = Club.objects.all()

    for temp_club in clubs:
        if request.user in temp_club.get_all_users():
            user_clubs_list.append(temp_club)

    config.user_clubs = user_clubs_list


@login_required
def club_list(request):
    clubs = []
    for club in Club.objects.all():
        clubs.append({
            "id": club.id,
            "name": club.get_name,
            "description": club.get_description,
            "location": club.get_location,
            "owner": club.get_owner,
            "meeting_online": club.meeting_online,
            "mini_gravatar": club.mini_gravatar(),
            "gravatar": club.gravatar()
        })
    return render(request, 'club_list.html', {'clubs': clubs})


@login_required
def club_selector(request):
    club_util(request)
    return render(request, "club_switcher.html", {'user_clubs': config.user_clubs})


@login_required
def club_selector_alt(request):
    club_util(request)
    return render(request, "club_switcher_alt.html", {"user_clubs": config.user_clubs})

@login_required
def new_club(request):  # new club adapted from the chess club project
    """ Create New Club """
    if request.method == 'POST':
        form = ClubForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            club_util(request)
            return redirect('club_list')
    else:
        form = ClubForm()
    return render(request, 'new_club.html', {'form':form})


class ClubsListView(LoginRequiredMixin, ListView):
    """View that shows a list of all clubs."""

    model = Club
    template_name = "club_list.html"
    context_object_name = "clubs"
    queryset = Club.objects.all()
    paginate_by = settings.CLUBS_PER_PAGE


@login_required
def club_profile(request, club_id):
    """ Individual Club's Profile Page """
    club = Club.objects.get(id=club_id)
    current_user = request.user
    return render(request, 'club_profile.html',{'club':club, 'current_user':current_user})

@login_required
def leave_club(request , club_id):
    """Leave A Club """
    club = Club.objects.get(pk=club_id)
    current_user = request.user
    club.remove_from_club(current_user)
    return redirect('club_selector')
