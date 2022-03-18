"""Adapted from clucker project"""
"""Post creation views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView
from django.urls import reverse
from bookclub.forms import PostForm
from bookclub.models import Post , Club , User

class NewPostView(LoginRequiredMixin, CreateView):
    """Class-based generic view for new post handling."""

    model = Post
    template_name = 'feed.html'
    form_class = PostForm
    http_method_names = ['post']
    context_object_name = 'club'


    def get_context_data(self, **kwargs):
        """Return context data, including new post form."""
        current_club_id = self.kwargs['club_id']
        current_club = Club.objects.get(id=current_club_id)
        current_user = self.request.user
        authors = current_user
        posts = Post.objects.filter(club=current_club)
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['form'] = PostForm()
        context['club'] = current_club_id
        context['posts'] = posts
        return context

    def form_valid(self, form , **kwargs):
        """Process a valid form."""
        current_club_id = self.kwargs['club_id']
        club = Club.objects.get(id=current_club_id)
        current_user = self.request.user
        form.instance.author = current_user
        form.save(club , current_user)
        return super().form_valid(form)

    def get_success_url(self ,**kwargs):
        """Return URL to redirect the user too after valid form handling."""
        club = Club.objects.all().get(pk=current_club_id)
        return reverse('feed', {"club": club})

    def handle_no_permission(self):
        return redirect('login')
