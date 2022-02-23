"""Club related views."""
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from bookclub.templates import *
from bookclub.forms import ApplicantForm, ApplicationForm, ScheduleMeetingForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView
from bookclub.models import User, Club, Application
from bookclub.views import club_views
from django.views.generic.edit import View
from django.core.paginator import Paginator


class ApplicationsView(LoginRequiredMixin, View):
    """View that handles club applications."""

    def get(self, request):
        """Display application template"""
        return self.render()

    def render(self):
        current_user = self.request.user
        """Render all applications of this user's owned clubs"""
        applicants = []

        owned_clubs = Club.objects.filter(owner=current_user)

        for a in Application.objects.all():
            if a.club in owned_clubs:
                applicants.append(a)

        return render(self.request, 'applications.html', {'applicants': applicants})


class MyApplicationsView(LoginRequiredMixin, View):
    """View that handles the currently logged in user's applications (as opposed to applications of their own clubs"""

    http_method_names = ['get']

    def get(self, request):
        """Display application template"""
        return self.render()

    def render(self):
        current_user = self.request.user
        """Render all applications of this user's owned clubs"""
        clubs = []
        my_applications = []
        for c in Club.objects.all():
            if c.owner is not current_user:
                clubs.append(c)

        for a in Application.objects.all():
            if a.club in clubs and a.applicant == current_user:
                my_applications.append(a)

        return render(self.request, 'my_applications.html', {'applications': my_applications})

class ClubMemberListView(LoginRequiredMixin, ListView):
    """Gets the members of each club"""
    
    model = Club
    template_name = "club_members.html"
    context_object_name = "club"
    paginate_by = settings.CLUBS_PER_PAGE
    
    def get_queryset(self):
        return Club.objects.filter(id=self.kwargs['club_id'])
    
        

def app_accept(request, pk):
    """Accept application"""
    app = Application.objects.all().get(pk=pk)
    app.club.make_member(app.applicant)
    app.delete()
    messages.add_message(request, messages.SUCCESS, "User accepted!")
    club_views.club_util(request)
    return redirect('applications')


def app_remove(request, pk):
    """Reject application"""
    app = Application.objects.all().get(pk=pk)
    app.delete()
    messages.add_message(request, messages.SUCCESS, "User rejected!")
    return redirect('applications')

@login_required
def new_application(request, club_id):
    """ Create A New Application """

    club_applied_to = Club.objects.get(pk=club_id)
    application_is_possible = True

    if request.method == 'POST':
        current_members = club_applied_to.get_all_users()
        if request.user in current_members:
            application_is_possible = False

        current_applications = Application.objects.filter(applicant=request.user, club=club_applied_to).count()
        if current_applications:
            application_is_possible = False

        if application_is_possible:
            Application.objects.create(
                applicant=request.user,
                club=club_applied_to
            )
            messages.add_message(request, messages.SUCCESS,
                                 f"Application to {Club.objects.get(pk=club_id).name} was successfully submitted!")

        else:
            messages.add_message(request, messages.ERROR,
                                 f"Could not apply to the following club: {Club.objects.get(pk=club_id).name}. You have "
                                 f"already applied.")


    return redirect('my_applications')


class MeetingScheduler(LoginRequiredMixin, View):
    """View that handles meeting scheduling."""

    http_method_names = ['get', 'post']

    def get(self, request, pk):
        """Display meeting scheduler template"""
        return self.render(pk)

    def post(self, request, pk):
        """Handle scheduling attempt."""

        current_club=Club.objects.get(pk=pk)
        form = ScheduleMeetingForm(club=current_club, data=request.POST)
        if form.is_valid():
            meeting = form.save(club=current_club)
            messages.add_message(request, messages.SUCCESS, "The meeting was scheduled!")
            return redirect('home')
        messages.add_message(request, messages.ERROR, "The meeting was unable to be scheduled!")
        return self.render(pk)

    def render(self, pk):
        """Render meeting scheduler form"""
        current_club=Club.objects.get(pk=pk)
        form = ScheduleMeetingForm(club=current_club)
        return render(self.request, 'schedule_meeting.html', {'form': form, 'pk':pk})
