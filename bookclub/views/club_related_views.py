"""Club related views."""
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from bookclub.templates import *
from bookclub.forms import  ApplicantForm
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
        """Render password club template with blank form"""     
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
    app = Application.objects.all().get(pk=pk)
    app.club.make_member(app.applicant)
    app.delete()
    return redirect('applications')

def app_remove(request, pk):
    app = Application.objects.all().get(pk=pk)
    app.delete()
    return redirect('applications')
