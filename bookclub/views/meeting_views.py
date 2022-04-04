"""Meeting related views."""
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from bookclub.templates import *
from bookclub.forms import ScheduleMeetingForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import ListView
from bookclub.models import Meeting, Club, Post
from bookclub.views import club_views
from django.views.generic.edit import View, UpdateView
from django.core.paginator import Paginator



class ClubMeetingsListView(LoginRequiredMixin, ListView):
    """Gets the meetings history of each club"""
    """Adapted from ClubMembersListView"""

    model = Club
    template_name = "club_meetings.html"
    paginate_by = settings.USERS_PER_PAGE
    pk_url_kwarg = 'club_id'
    context_object_name = 'club'
    ordering = ['-meeting.date']

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to clubs list if club_id invalid."""
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('home')

    def get_queryset(self):
        return Club.objects.get(id=self.kwargs['club_id']).get_meetings()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        current_club_id = self.kwargs['club_id']
        current_club = Club.objects.get(id=current_club_id)
        paginator = Paginator(current_club.get_meetings(), settings.USERS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['club'] = current_club
        context['page_obj'] = page_obj
        return context


# @login_required
# def meetings_list(request, club_id):
#     club = Club.objects.get(id=club_id)
#     meetings = club.get_meetings()
#     paginator = Paginator(meetings, 2)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     return render(request, 'club_meetings.html', {'club': club, 'page_obj': page_obj})


class MeetingScheduler(LoginRequiredMixin, View):
    """View that handles meeting scheduling."""

    http_method_names = ['get', 'post']

    def get(self, request, pk):
        """Display meeting scheduler template"""
        return self.render(pk)

    def post(self, request, pk):
        """Handle scheduling attempt."""

        current_club = Club.objects.get(pk=pk)
        form = ScheduleMeetingForm(club=current_club, data=request.POST)
        if form.is_valid():
            meeting = form.save(club=current_club)
            messages.add_message(request, messages.SUCCESS, "The meeting was scheduled!")
            date = form.cleaned_data['date'].strftime("%d/%m/%y")
            time = form.cleaned_data['start_time'].strftime("%H:%M")
            msg = "New meeting scheduled on " + date + " at " + time + "."
            Post.objects.create(author=request.user, club=current_club, text=msg)
            return redirect('club_profile', pk)
        messages.add_message(request, messages.ERROR, "The meeting was unable to be scheduled!")
        return self.render(pk)

    def render(self, pk):
        """Render meeting scheduler form"""
        current_club = Club.objects.get(pk=pk)
        form = ScheduleMeetingForm(club=current_club)
        if self.request.user == current_club.owner or (
                self.request.user in current_club.get_organisers() and current_club.organiser_owner):
            return render(self.request, 'schedule_meeting.html', {'form': form, 'pk': pk})
        else:
            messages.add_message(self.request, messages.ERROR, "Action prohibited")
            return redirect('club_list')


class MeetingUpdateView(LoginRequiredMixin, UpdateView):
    """View to update a scheduled club meeting
    
    Adapted from Raisa Ahmed's ProfileUpdateView"""

    model = ScheduleMeetingForm
    template_name = "edit_meeting.html"
    form_class = ScheduleMeetingForm

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Meeting updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    def form_vaild(self, form):
        club = form.instance.club
        form.save(club)
        return super().form_valid(form)

    def post(self, request, club_id, meeting_id, *args, **kwargs):
        club = Club.objects.get(id=club_id)
        meeting = Meeting.objects.get(id=meeting_id)
        form = self.form_class(instance=meeting, club=club, data=request.POST)
        if form.is_valid():
            old_meeting = Meeting.objects.get(id=meeting_id)
            old_date = old_meeting.date.strftime("%d/%m/%y")
            old_time = old_meeting.start_time.strftime("%H:%M")
            new_date = form.cleaned_data['date'].strftime("%d/%m/%y")
            new_time = form.cleaned_data['start_time'].strftime("%H:%M")
            msg = "The meeting scheduled for " + old_date + " at " + old_time + " has been rescheduled to " + new_date + " at " + new_time + "."
            old_meeting.delete()
            Post.objects.create(author=request.user, club=club, text=msg)
            form.save(club)
            self.get_success_url()
            return redirect('home')

        messages.add_message(self.request, messages.ERROR, form.errors['__all__'].as_text())
        return render(request, 'edit_meeting.html', {"club": club, "form": form})

    def get(self, request, club_id, meeting_id, *args, **kwargs):
        club = Club.objects.get(id=club_id)
        meeting = Meeting.objects.get(id=meeting_id)
        if self.request.user == club.owner or (
                self.request.user in club.get_organisers() and club.organiser_owner):
                form = self.form_class(instance=meeting, club=club)
                return render(request, 'edit_meeting.html', {"club": club, "form": form})
        else:
            messages.add_message(self.request, messages.ERROR, "Action prohibited")
            return redirect('club_list')

@login_required
def remove_from_meeting_list(request, club_id, meeting_id, *args, **kwargs):
    club = Club.objects.get(id=club_id)
    meeting = Meeting.objects.get(id=meeting_id)
    old_date = meeting.date.strftime("%d/%m/%y")
    old_time = meeting.start_time.strftime("%H:%M")
    msg = "The meeting scheduled for " + old_date + " at " + old_time + " has been cancelled."
    meeting.delete()
    Post.objects.create(author=request.user, club=club, text=msg)
    messages.add_message(request, messages.ERROR, f"The meeting has been cancelled")
    return redirect("club_meetings", club_id = club_id)