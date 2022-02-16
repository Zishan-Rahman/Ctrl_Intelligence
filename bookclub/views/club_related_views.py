"""Club related views."""
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from bookclub.templates import *
from bookclub.forms import  ApplicantForm, ScheduleMeetingForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic.edit import View
from bookclub.models import User, Club, Application


class ApplicationsView(LoginRequiredMixin, View):
    """View that handles club applications."""

    http_method_names = ['get']

    def get(self, request):
        """Display application template"""
        return self.render()

    def render(self):
        current_user = self.request.user
        """Render all applications of this user's owned clubs"""     
        owned_clubs = []
        applicants = []
        for c in Club.objects.all():
            if c.owner == current_user:
                owned_clubs.append(c)
        
        for a in Application.objects.all():
            if a.club in owned_clubs:
                applicants.append(a)
                                                                                                                               
        return render(self.request, 'applications.html', {'applicants': applicants})


def app_accept(request, pk):
    """Accept application"""
    app = Application.objects.all().get(pk=pk)
    app.club.make_member(app.applicant)
    app.delete()
    messages.add_message(request, messages.SUCCESS, "User accepted!")
    return redirect('applications')

def app_remove(request, pk):
    """Reject application"""
    app = Application.objects.all().get(pk=pk)
    app.delete()
    messages.add_message(request, messages.SUCCESS, "User rejected!")
    return redirect('applications')


class MeetingScheduler(LoginRequiredMixin, View):
    """View that handles meeting scheduling."""

    http_method_names = ['get', 'post']

    def get(self, request):
        """Display meeting scheduler template"""
        return self.render()

    def post(self, request):
        """Handle scheduling attempt."""

        form = ScheduleMeetingForm(request.POST)
        current_club=Club.objects.all()[0] #Change as soon as club profile is done
        if form.is_valid():
            meeting = form.save(club=current_club)
            messages.add_message(request, messages.SUCCESS, "The meeting was scheduled!")
            return redirect('home')
        messages.add_message(request, messages.ERROR, "The meeting was unable to be scheduled!")
        return self.render()

    def render(self):
        """Render meeting scheduler form"""  

        form = ScheduleMeetingForm()
        return render(self.request, 'schedule_meeting.html', {'form': form})
