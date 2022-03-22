from django.conf import settings
from django.db.models import Q
from django.contrib import messages
from bookclub.templates import *
from django.shortcuts import render, redirect
from django.urls import reverse
from bookclub.models import User, Club, Message, Chat
from bookclub.forms import UserForm
from django.contrib.auth import login
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import Http404, JsonResponse
from bookclub.views import config
import re


@login_required
def user_list(request):
    users = []
    for user in User.objects.all():
        users.append({
            "id": user.id,
            "first_name": user.get_first_name,
            "last_name": user.get_last_name,
            "email": user.get_email,
            "public_bio": user.get_bio,
            "favourite_genre" : user.get_favourite_genre,
            "mini_gravatar": club.mini_gravatar(),
            "gravatar": club.gravatar()
        })
    return render(request, 'user_list.html', {'users': users})

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


class UsersListView(LoginRequiredMixin, ListView):
    """View that shows a list of all books."""

    model = User
    template_name = "user_list.html"
    context_object_name = "users"
    queryset = User.objects.all()
    paginate_by = settings.USERS_PER_PAGE



@login_required
def user_profile(request, user_id):
    """ Individual User's Profile Page """
    club_util(request)
    user = User.objects.get(id = user_id)
    current_user = request.user
    following = request.user.is_following(user)
    followable = request.user != user
    return render(request, 'user_profile.html',{'user': user,
                            'current_user':current_user,
                            'following': following,
                            'followable':followable,
                            'user_clubs': config.user_clubs}
    )

@login_required
def follow_toggle(request, user_id):
    current_user = request.user
    followee = User.objects.get(id = user_id)
    current_user.toggle_follow(followee)
    return redirect('user_profile', user_id = user_id)


def club_util(request):
    user_clubs_list = []
    clubs = Club.objects.all()

    for temp_club in clubs:
        if request.user in temp_club.get_all_users():
            user_clubs_list.append(temp_club)

    config.user_clubs = user_clubs_list


@login_required
def inviteMessage(request, user_id, club_id):
    link = reverse('club_profile', kwargs={'club_id': club_id})
    club = Club.objects.get(pk=club_id)
    receiver = User.objects.get(pk=user_id)
    chat_query = Chat.objects.filter(user=request.user, receiver=receiver)
    if chat_query:
        chat = chat_query.get()
    else:
        chat = Chat(user=request.user, receiver=receiver)
        chat.save()
    message = Message(
    chat=chat,
    sender_user=request.user,
    receiver_user=receiver,
    body=(f"Hi {receiver.first_name}, {request.user.first_name} invited you to join the club {club.name}. To view the club page, please click the link below: {link} "))
    message.save()
    return redirect('user_profile', user_id = user_id)
