"""Adapted from clucker project"""
"""Post creation views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView
from django.urls import reverse
from bookclub.forms import UserPostForm
from bookclub.models import UserPost, Club, User
from django.contrib import messages


class UserNewPostView(LoginRequiredMixin, CreateView):
    """Class-based generic view for new post handling."""

    model = UserPost
    template_name = 'user_feed.html'
    form_class = UserPostForm
    http_method_names = ['post']
    context_object_name = 'user'


    def get_context_data(self, **kwargs):
        """Return context data, including new post form."""
        user = self.request.user
        user_posts = UserPost.objects.filter(author = user)
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['form'] = UserPostForm()
        context['posts'] = user_posts
        return context

    def form_valid(self, form, **kwargs):
        """Process a valid form."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        """Return URL to redirect the user too after valid form handling."""
        messages.add_message(self.request, messages.SUCCESS, "The post was sent!")
        return reverse('profile')

    def handle_no_permission(self):
        return redirect('login')
