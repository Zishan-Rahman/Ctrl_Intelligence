"""Adapted from clucker project"""
"""Post creation views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView
from django.urls import reverse
from bookclub.forms import PostForm
from bookclub.models import Post , Club

class NewPostView(LoginRequiredMixin, CreateView):
    """Class-based generic view for new post handling."""

    model = Post
    template_name = 'feed.html'
    form_class = PostForm
    http_method_names = ['post']
    pk_url_kwarg = 'club_id'

    def form_valid(self, form):
        """Process a valid form."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('feed')

    def handle_no_permission(self):
        return redirect('login')

    def post(self, request, *args, **kwargs):
        current_club_id = self.kwargs['club_id']
        club = Club.objects.all().get(pk=current_club_id)
        form = self.form_class(instance=club, data=request.POST)
        # authors = self.request.user
        posts = Post.objects.filter(club=club)
        if form.is_valid():
            form.save(club, request.user)
            form = PostForm()
            # return render('feed')
        return render(request, 'feed.html', {"author": request.user, "club": club, "form": form, "posts": posts})

    def get(self, request , *args, **kwargs):
        authors = self.request.user
        current_club_id = self.kwargs['club_id']
        club = Club.objects.all().get(pk=current_club_id)
        posts = Post.objects.filter(club=club)
        form = self.form_class(instance=club)
        return render(request, 'feed.html', {"author": request.user, "club": club, "form": form, "posts": posts})