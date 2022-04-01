from django.conf import settings
from django.db.models import Q
from django.contrib import messages
from django.template import context
from bookclub.templates import *
from django.shortcuts import render, redirect
from django.urls import reverse
from bookclub.models import User, Club, Message, Chat, UserPost
from bookclub.forms import UserForm, UserPostForm
from django.http import Http404
from django.contrib.auth import login
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.template.loader import render_to_string
from bookclub.views import config
from django.core.paginator import Paginator

class UserClubsListView(LoginRequiredMixin, ListView):
    """List of clubs owned by and participated by the user"""

    model = User
    template_name = "user_clubs.html"
    context_object_name = 'user'
    pk_url_kwarg = 'user_id'
    ordering = ['-name']
    paginate_by = settings.CLUBS_PER_PAGE

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to home if user_id invalid."""
        if self.kwargs['user_id'] == request.user.id:
            return redirect('club_selector')
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('home')

    def get_queryset(self):
        """Return the list of clubs for a specific user"""
        return User.objects.get(id=self.kwargs['user_id']).get_all_clubs()

    def get_context_data(self, *args, **kwargs):
        """Return keyword data for the view"""
        context = super().get_context_data(*args, **kwargs)
        queried_user_id = self.kwargs['user_id']
        queried_user = User.objects.get(id=queried_user_id)
        all_clubs = queried_user.get_all_clubs()
        paginator = Paginator(queried_user.get_all_clubs(), settings.CLUBS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['current_user'] = queried_user
        context['all_clubs'] = all_clubs
        context['page_obj'] = page_obj
        context['user'] = self.request.user
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View to update logged-in user's profile."""

    model = UserForm
    template_name = "edit_profile.html"
    form_class = UserForm

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse('profile')

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
    user = User.objects.get(id=user_id)
    club_util(request)
    current_user = request.user
    following = request.user.is_following(user)
    followable = request.user != user
    followers = request.user.followers.all()
    currently_reading_books = user.currently_reading_books.all()
    form = UserPostForm()
    posts = UserPost.objects.filter(author=user)
    posts = posts[:6]

    return render(request, 'user_profile.html',
                  {
                      'user': user,
                      'current_user': current_user,
                      'following': following,
                      'followable': followable,
                      'user_clubs': config.user_clubs,
                      'currently_reading_books': currently_reading_books[:3],
                      'form': form,
                      'posts': posts
                  }
                  )


@login_required
def current_user_profile(request):
    """ Current User's Profile Page """
    return user_profile(request, user_id=request.user.id)


@login_required
def follow_toggle(request, user_id):
    current_user = request.user
    followee = User.objects.get(id=user_id)
    if followee in current_user.get_users_followees():
        current_user.toggle_follow(followee)
        messages.add_message(request, messages.ERROR, f'You have unfollowed {followee.get_full_name()}!')
    else:
        current_user.toggle_follow(followee)
        messages.add_message(request, messages.SUCCESS, f'You now follow {followee.get_full_name()}!')


@login_required
def follow_from_user_list(request, user_id):
    follow_toggle(request, user_id)
    return redirect('user_list')


@login_required
def follow_from_user_profile(request, user_id):
    follow_toggle(request, user_id)
    return redirect('user_profile', user_id=user_id)


@login_required
def unfollow(request, user_id):
    current_user = request.user
    followee = User.objects.get(id=user_id)
    current_user._unfollow(followee)
    messages.add_message(request, messages.ERROR, f'You unfollowed {followee.get_full_name()}!')


@login_required
def unfollow_from_user_list(request, user_id):
    unfollow(request, user_id)
    return redirect('user_list')


@login_required
def unfollow_from_user_profile(request, user_id):
    unfollow(request, user_id)
    return redirect('user_profile', user_id=user_id)


def club_util(request):
    user_clubs_list = request.user.get_all_clubs()
    config.user_clubs = user_clubs_list


@login_required
def inviteMessage(request, user_id, club_id):
    club = Club.objects.get(pk=club_id)
    receiver = User.objects.get(pk=user_id)
    body = render_to_string('invite.html', {
        'receiver': receiver.first_name,
        'sender': request.user.first_name,
        'club_name': club.name})
    chat_query = Chat.objects.filter(user=request.user, receiver=receiver)
    r_chat_query = Chat.objects.filter(receiver=request.user, user=receiver)
    if chat_query:
        chat = chat_query.get()
    elif r_chat_query:
        chat = r_chat_query.get()
    else:
        chat = Chat(user=request.user, receiver=receiver)
        chat.save()
    message = Message(
        chat=chat,
        sender_user=request.user,
        receiver_user=receiver,
        body=body,
        club=club)
    message.save()
    messages.add_message(request, messages.SUCCESS, "Invite Sent!")
    return redirect('user_profile', user_id=user_id)
