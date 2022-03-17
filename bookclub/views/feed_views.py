"""Adapted from clucker project"""
"""Feed related views."""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from bookclub.forms import PostForm
from bookclub.models import Club, Post

class FeedView(LoginRequiredMixin, ListView):
    """Class-based generic view for displaying a view."""

    model = Post
    template_name = "feed.html"
    context_object_name = 'posts'
    pk_url_kwarg = 'club_id'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        """Return the user's feed."""
        current_user = self.request.user
        authors = current_user
        posts = Post.objects.filter(author=authors)
        return posts

    def get_context_data(self, **kwargs):
        """Return context data, including new post form."""
        current_club_id = self.kwargs['club_id']
        current_club = Club.objects.get(id=current_club_id)
        current_user = self.request.user
        authors = current_user
        posts = Post.objects.filter(author=authors)
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['form'] = PostForm()
        context['club'] = current_club_id
        context['posts'] = posts
        return context