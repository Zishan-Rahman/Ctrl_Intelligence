from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from bookclub.forms import ClubForm
from bookclub.models import Club

@login_required
def club_list(request):
    clubs = []
    for club in Club.objects.all():
        clubs.append({
            "name": club.get_name,
            "description": club.get_description,
            "location": club.get_location,
        })
    return render(request, 'club_list.html', {'clubs':clubs})

@login_required
def new_club(request):     # new club adapted from the chess club project
    """ Create New Club """
    if request.method == 'POST':
        form = ClubForm(request.POST)
        if form.is_valid():
            club = form.save(request.user)
            return redirect('club_list')
    else:
        form = ClubForm()
    return render(request, 'new_club.html', {'form':form})