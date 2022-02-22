"""Account related views."""
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from bookclub.templates import *
from bookclub.forms import PasswordForm, UserForm
from bookclub.models import Club, User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import MultipleObjectMixin

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'landing_page.html')

@login_required
def user_list(request):
    users = User.objects.all()
    all_users = Club.get_all_users
    return render(request, 'user_list.html', {'users': users})

@login_required
def user_profile(request):
    """ Individual User's Profile Page """
    user = User.objects.get(id = request.user.id)
    current_user = request.user
    return render(request, 'user_profile.html',{'user': user})


class UsersListView(LoginRequiredMixin, ListView):
    """View that shows a list of all books."""

    model = User
    template_name = "user_list.html"
    context_object_name = "users"
    queryset = User.objects.all()
    paginate_by = settings.USERS_PER_PAGE

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View to update logged-in user's profile."""

    model = UserForm
    template_name = "edit_profile.html"
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
        form = self.form_class(instance=current_user, data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return render(request, 'edit_profile.html', {"form": form})

    def get(self, request, *args, **kwargs):
        current_user = request.user
        form = self.form_class(instance=current_user)
        return render(request, 'edit_profile.html', {"form": form})


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
        form = self.form_class(user=current_user,data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return render(request, 'password.html', {"form": form})


    def get(self, request, *args, **kwargs):
        current_user = request.user
        form = self.form_class()
        return render(request, 'password.html', {"form": form})
