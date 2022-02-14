"""Clubs related views."""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import ListView
from bookclub.forms import ClubForm
from bookclub.models import Club
#
# @login_required
# def club_list(request):
#     memberships = Club.objects.filter(members=request.user) | Club.objects.filter(organisers=request.user) | Club.objects.filter(owner=request.user)
#     clubs = []
#     for club in Club.objects.all():
#         clubs.append({
#             "name": club.get_name,
#             "description": club.get_description,
#             "location": club.get_location,
#         })
#     return render(request, 'club_list.html', {'clubs':clubs, "club_memberships": memberships})

# @login_required
# def club_list(request):
#     memberships = Club.objects.filter(members=request.user) | Club.objects.filter(organisers=request.user) | Club.objects.filter(owner=request.user)
#     clubs = []
#     for club in Club.objects.all():
#         clubs.append({
#             "name": club.get_name,
#             "description": club.get_description,
#             "location": club.get_location,
#             "mini_gravatar": club.mini_gravatar(),
#             "gravatar": club.gravatar()
#         })
#     return render(request, 'club_list.html', {'clubs':clubs, "club_memberships": memberships})

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


class ClubsListView(LoginRequiredMixin, ListView):
    """View that shows a list of all books."""

    model = Club
    template_name = "club_list.html"
    context_object_name = "clubs"
    queryset = Club.objects.all()
    paginate_by = settings.CLUBS_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        memberships = Club.objects.filter(members=self.request.user) | Club.objects.filter(organisers=self.request.user) | Club.objects.filter(owner=self.request.user)
        context['club_memberships'] = memberships
        return context
