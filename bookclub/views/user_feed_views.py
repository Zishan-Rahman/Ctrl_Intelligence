"""Adapted from clucker project"""
"""Feed related views."""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import ListView, FormView
from bookclub.forms import UserPostForm
from bookclub.models import User , UserPost , Club


class UserFeedView(LoginRequiredMixin, ListView):
    """Class-based generic view for displaying a view."""

    model = UserPost
    template_name = "user_feed.html"
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        """Return context data, including new post form."""
        current_club_id = self.kwargs['club_id']
        current_club = Club.objects.get(id=current_club_id)
        current_user = self.request.user
        authors = current_user
        posts = UserPost.objects.filter(author= authors)
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['form'] = UserPostForm()
        context['club'] = current_club_id
        context['posts'] = posts
        return context

    def post(self, request, *args, **kwargs):
        current_club_id = self.kwargs['club_id']
        club = Club.objects.all().get(pk=current_club_id)
        authors = self.request.user
        form = UserPostForm()
        posts = UserPost.objects.filter(author = authors)
        if form.is_valid():
            return redirect('user_feed')
        return render(request, 'user_feed.html', {"author": request.user, "club": club, "form": form, "posts": posts})

    def get(self, request, *args, **kwargs):
        current_club_id = self.kwargs['club_id']
        club = Club.objects.all().get(pk=current_club_id)
        authors = self.request.user
        posts = UserPost.objects.filter(author = authors)
        form = UserPostForm()
        return render(request, 'user_feed.html', {"author": request.user, "club": club, "form": form, "posts": posts})
