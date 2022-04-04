"""Adapted from clucker project"""
"""Post creation views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView
from django.urls import reverse
from bookclub.forms import UserPostForm
from bookclub.models import UserPost, Club, User
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import View
from django.core.paginator import Paginator
from django.conf import settings



class UserNewPostView(LoginRequiredMixin, CreateView):
    """Class-based generic view for new post handling."""

    model = UserPost
    template_name = 'user_feed.html'
    form_class = UserPostForm
    http_method_names = ['post']
    context_object_name = 'user'
    pk_url_kwarg = 'user_id'


    def get_context_data(self, **kwargs):
        """Return context data, including new post form."""
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        user_posts = UserPost.objects.filter(author = user)
        context = super().get_context_data(**kwargs)
        context['user'] = user_id
        context['form'] = UserPostForm()
        context['posts'] = user_posts
        return context

    def form_valid(self, form, **kwargs):
        """Process a valid form."""
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        form.instance.author = user
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        """Return URL to redirect the user too after valid form handling."""
        messages.add_message(self.request, messages.SUCCESS, "The post was sent!")
        user = self.kwargs['user_id']
        return reverse('profile')

    def handle_no_permission(self):
        return redirect('login')

def get_all_follow_posts(request):
    all_follow_posts = []
    current_user = request.user

    for follow in current_user.followees.all():
        user_posts = list(set(UserPost.objects.filter(author=follow)))
        if user_posts:
            for post in user_posts:
                all_follow_posts.append(post)
    all_follow_posts.sort(key=lambda p: p.created_at, reverse=True)
    return all_follow_posts

class UserPostsView(LoginRequiredMixin, View):
    """View that handles user posts."""

    def get(self, request):
        """Display user post template"""
        return self.render()

    def render(self):
        current_user = self.request.user
        """Render all user posts"""
        user_posts = get_all_follow_posts(self.request)

        paginator = Paginator(user_posts, settings.POSTS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(self.request, 'user_posts.html', {'user_posts': user_posts, 'page_obj': page_obj})
