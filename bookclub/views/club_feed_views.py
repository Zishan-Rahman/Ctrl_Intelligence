"""Adapted from clucker project"""
"""Club Feed related views."""
from bookclub.models import Club, Post
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import ListView, FormView
from bookclub.forms import PostForm

class ClubFeedView(LoginRequiredMixin, ListView):

    """Class-based generic view for displaying a view."""

    model = Post
    template_name = "feed.html"
    context_object_name = 'posts'
    pk_url_kwarg = 'club_id'
    paginate_by = settings.POSTS_PER_PAGE

    def get_context_data(self, **kwargs):
        """Return context data, including new post form."""
        current_club_id = self.kwargs['club_id']
        current_club = Club.objects.get(id=current_club_id)
        current_user = self.request.user
        paginator = Paginator(current_club.get_posts(), settings.POSTS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        authors = current_user
        posts = Post.objects.filter(club=current_club)
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['form'] = PostForm()
        context['club'] = current_club_id
        context['posts'] = posts
        context['page_obj'] = page_obj
        return context

    def post(self, request, *args, **kwargs):
        current_club_id = self.kwargs['club_id']
        club = Club.objects.all().get(pk=current_club_id)
        form = PostForm()
        posts = Post.objects.filter(club=club)
        paginator = Paginator(posts, settings.POSTS_PER_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if form.is_valid():
            return redirect('feed')
        return render(request, 'feed.html', {"author": request.user, "club": club, "form": form, "posts": posts, 'page_obj': page_obj})

    def get(self, request, *args, **kwargs):
        current_club_id = self.kwargs['club_id']
        club = Club.objects.all().get(pk=current_club_id)
        posts = Post.objects.filter(club=club)
        paginator = Paginator(posts, settings.POSTS_PER_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        form = PostForm()
        return render(request, 'feed.html', {"author": request.user, "club": club, "form": form, "posts": posts, 'page_obj': page_obj})
