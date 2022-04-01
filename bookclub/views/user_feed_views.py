"""Adapted from clucker project"""
"""Feed related views."""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import ListView, FormView
from django.core.paginator import Paginator
from bookclub.forms import UserPostForm
from bookclub.models import User, UserPost, Club



class UserFeedView(LoginRequiredMixin, ListView):
    """Class-based generic view for displaying a view."""

    model = UserPost
    template_name = "user_feed.html"
    context_object_name = 'posts'
    pk_url_kwarg = 'user_id'
    paginate_by = settings.POSTS_PER_PAGE

    def get_context_data(self, **kwargs):
        """Return context data, including new post form."""
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        author = user
        context = super().get_context_data(**kwargs)
        context['user'] = user_id
        context['form'] = UserPostForm()
        return context

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        form = UserPostForm()
        posts = UserPost.objects.filter(authors=user)
        paginator = Paginator(posts, settings.POSTS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if form.is_valid():
            return redirect('user_feed')
        return render(request, 'user_feed.html', {"user": user, "form": form, "posts": posts, "page_obj": page_obj})

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        posts = UserPost.objects.filter(author=user)
        form = UserPostForm()
        paginator = Paginator(posts, settings.POSTS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'user_feed.html', {"user": user, "form": form, "posts": posts, "page_obj":page_obj})
