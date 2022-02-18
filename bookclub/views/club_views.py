from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from bookclub.forms import ClubForm
from bookclub.models import Club
from bookclub.views import config

def club_util(request):
    user_clubs_list = []
    clubs = Club.objects.all()

    for temp_club in clubs:
        if request.user in temp_club.get_all_users():
            user_clubs_list.append(temp_club)

    config.user_clubs = user_clubs_list


@login_required
def club_list(request):
    memberships = Club.objects.filter(members=request.user) | Club.objects.filter(organisers=request.user) | Club.objects.filter(owner=request.user)
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
    return render(request, 'club_list.html', {'clubs':clubs, "club_memberships": memberships})


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

@login_required
def club_profile(request, club_id):
    """ Individual Club's Profile Page """
    club = Club.objects.get(id = club_id)
    return render(request, 'club_profile.html',{'club':club})
