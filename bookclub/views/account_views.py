"""Account related views."""
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from bookclub.templates import *
from bookclub.forms import PasswordForm, UserForm
from bookclub.models import Club
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic.edit import FormView, UpdateView

def landing_page(request):
    return render(request, 'landing_page.html')

@login_required
def user_list(request):

    all_users = Club.get_all_users
    memberships = Club.objects.filter(members=request.user) | Club.objects.filter(organisers=request.user) | Club.objects.filter(owner=request.user)
    return render(request, 'user_list.html', {"club_memberships": memberships})

@login_required
def club_list(request):
    memberships = Club.objects.filter(members=request.user) | Club.objects.filter(organisers=request.user) | Club.objects.filter(owner=request.user)
    return render(request, 'club_list.html', {"club_memberships": memberships})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View to update logged-in user's profile."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    def post(self, request, *args, **kwargs):
        current_user = request.user
        memberships = Club.objects.filter(members=request.user) | Club.objects.filter(organisers=request.user) | Club.objects.filter(owner=request.user)
        form = self.form_class(instance=current_user, data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return render(request, 'profile.html', {"form": form, "club_memberships": memberships})

    def get(self, request, *args, **kwargs):
        current_user = request.user
        memberships = Club.objects.filter(members=request.user) | Club.objects.filter(organisers=request.user) | Club.objects.filter(owner=request.user)
        form = self.form_class(instance=current_user)
        return render(request, 'profile.html', {"form": form,"club_memberships": memberships})


class PasswordView(LoginRequiredMixin, FormView):
    """View that handles password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('home')

    def post(self, request, *args, **kwargs):
        current_user = request.user
        memberships = Club.objects.filter(members=request.user) | Club.objects.filter(organisers=request.user) | Club.objects.filter(owner=request.user)
        form = self.form_class(user=current_user,data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return render(request, 'password.html', {"form": form,"club_memberships": memberships})


    def get(self, request, *args, **kwargs):
        current_user = request.user
        memberships = Club.objects.filter(members=request.user) | Club.objects.filter(organisers=request.user) | Club.objects.filter(owner=request.user)
        form = self.form_class()
        return render(request, 'password.html', {"form": form, "club_memberships": memberships})
