"""Adapted from clucker project"""
"""Post creation views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView
from django.urls import reverse
from bookclub.forms import PostForm
from bookclub.models import Post, Club, User
from bookclub.views import config
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import View
from django.core.paginator import Paginator
from django.conf import settings



class NewPostView(LoginRequiredMixin, CreateView):
    """Class-based generic view for new post handling."""

    model = Post
    template_name = 'feed.html'
    form_class = PostForm
    http_method_names = ['post']
    context_object_name = 'club'
    pk_url_kwarg = 'club_id'

    def get_context_data(self, **kwargs):
        """Return context data, including new post form."""
        current_club_id = self.kwargs['club_id']
        current_club = Club.objects.get(id=current_club_id)
        posts = Post.objects.filter(club=current_club)
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['form'] = PostForm()
        context['club'] = current_club_id
        context['posts'] = posts
        return context

    def form_valid(self, form, **kwargs):
        """Process a valid form."""
        current_club_id = self.kwargs['club_id']
        club = Club.objects.get(id=current_club_id)
        form.instance.author = self.request.user
        form.instance.club = club
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        """Return URL to redirect the user too after valid form handling."""
        messages.add_message(self.request, messages.SUCCESS, "The post was sent!")
        current_club_id = self.kwargs['club_id']
        return reverse('club_profile', kwargs={'club_id': current_club_id})

    def handle_no_permission(self):
        return redirect('login')

def club_util(request):
    user_clubs_list = []
    clubs = Club.objects.all()

    for temp_club in clubs:
        if request.user in temp_club.get_all_users():
            user_clubs_list.append(temp_club)

    config.user_clubs = user_clubs_list

def get_all_club_posts(request):

    user_clubs_list = []
    clubs = Club.objects.all()

    for club in clubs:
        if request.user in club.get_all_users():
            user_clubs_list.append(club)

    all_club_posts = []

    for club in user_clubs_list:
        club_posts = list(set(Post.objects.filter(club=club)))
        if club_posts:
            for post in club_posts:
                all_club_posts.append(post)
    all_club_posts.sort(key=lambda p: p.created_at, reverse=True)
    return all_club_posts

class ClubPostsView(LoginRequiredMixin, View):
    """View that handles club posts."""

    def get(self, request):
        """Display club post template"""
        return self.render()

    def render(self):
        current_user = self.request.user
        """Render all club posts"""
        club_posts = get_all_club_posts(self.request)

        paginator = Paginator(club_posts, settings.POSTS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(self.request, 'club_posts.html', {'club_posts': club_posts, 'page_obj': page_obj})
