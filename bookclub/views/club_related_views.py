"""Club related views."""
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from bookclub.templates import *
from bookclub.forms import  ApplicantForm, ApplicationForm
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
        paginator = Paginator(applicants, 1)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(self.request, 'applications.html', {'page_obj': page_obj, 'applicants' : applicants})


# class ApplicationsView(LoginRequiredMixin, ListView):
#     """View that handles club applications."""
#
#     model = Application
#     template_name = "applications.html"
#     context_object_name = "applicants"
#     #queryset = Application.objects.all()
#     paginate_by = settings.APPLICATIONS_PER_PAGE
#
#     def get(self, request):
#         """Display application template"""
#         return self.render()
#
#     # def get_context_data(self, **kwargs):
#     #     context = super().get_context_data(**kwargs)
#     #     current_user = self.request.user
#     #     owned_clubs = []
#     #     applicants = []
#     #     for c in Club.objects.all():
#     #         if c.owner == current_user:
#     #             owned_clubs.append(c)
#     #     for a in Application.objects.all():
#     #         if a.club in owned_clubs:
#     #             applicants.append(a)
#     #     context['applicants'] = applicants
#     #     memberships = Club.objects.filter(members=current_user) | Club.objects.filter(organisers=current_user) | Club.objects.filter(owner=current_user)
#     #     context['club_memberships'] = memberships
#     #     #context['applicants'] = applicants
#     #     return context
#     #
#     def render(self):
#         current_user = self.request.user
#         """Render all applications of this user's owned clubs"""
#         owned_clubs = []
#         applicants = []
#         for c in Club.objects.all():
#             if c.owner == current_user:
#                 owned_clubs.append(c)
#
#         for a in Application.objects.all():
#             if a.club in owned_clubs:
#                 applicants.append(a)
#
#         return render(self.request, 'applications.html', {'applicants': applicants})

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
    form = ApplicationForm(request.POST)
    if form.is_valid():
        application = form.save(request.user) #TODO: Get the application to save into the database and get read from the applications view
        messages.add_message(request, messages.SUCCESS, f"Application to {Club.objects.get(pk=club_id).name} was successfully submitted!")
    else:
        messages.add_message(request, messages.ERROR, f"Could not apply to the following club: {Club.objects.get(pk=club_id).name}")
    return redirect('applications')
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


    return render(request, "club_list.html")
