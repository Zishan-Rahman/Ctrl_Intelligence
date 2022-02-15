from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from bookclub.forms import ClubForm
from bookclub.models import Club

@login_required
def club_list(request):
    memberships = Club.objects.filter(members=request.user) | Club.objects.filter(organisers=request.user) | Club.objects.filter(owner=request.user)
    clubs = []
    for club in Club.objects.all():
        clubs.append({
            "name": club.get_name,
            "description": club.get_description,
            "location": club.get_location,
            "meeting_online": club.meeting_online,
            "mini_gravatar": club.mini_gravatar(),
            "gravatar": club.gravatar()
        })
    return render(request, 'club_list.html', {'clubs':clubs, "club_memberships": memberships})

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

@login_required
def club_profile(request, club_id):
    """ Individual Club's Profile Page """
    club = Club.objects.get(id = club_id)
    #owner= Ownership.objects.get(club = club.id).owner
    #members = []
    #for membership in Membership.objects.all().filter(club = club):
        #for member in membership.member.all():
            #members.append(member)

    # officers = []
    # for worksfor in WorksFor.objects.all().filter(club = club):
    #     for officer in worksfor.officer.all():
    #         officers.append(officer)


    #clubs_already_applied = []
    #for application in Application.objects.all():
        #if application.applicant_id == request.user.id:
            #clubs_already_applied.append(application.club)

    # members_number = Membership.objects.all().filter(club=club).count() + WorksFor.objects.all().filter(club=club).count() + 1

    return render(request, 'club_profile.html',{'club':club})
