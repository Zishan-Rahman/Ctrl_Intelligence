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
        posts = UserPost.objects.filter(author = user)
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['form'] = UserPostForm()
        context['posts'] = posts
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        form = UserPostForm()
        posts = UserPost.objects.filter(authors = user)
        if form.is_valid():
            return redirect('user_feed')
        return render(request, 'user_feed.html', {"user": request.user, "form": form, "posts": posts})

    def get(self, request, *args, **kwargs):
        user = self.request.user
        posts = UserPost.objects.filter(author = user)
        form = UserPostForm()
        return render(request, 'user_feed.html', {"user": request.user, "form": form, "posts": posts})
