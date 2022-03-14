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
from bookclub.models import Meeting, Club
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
        return Club.objects.get(id = self.kwargs['club_id']).get_meetings()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        current_club_id = self.kwargs['club_id']
        current_club = Club.objects.get(id = current_club_id)
        paginator = Paginator(current_club.get_meetings(), settings.USERS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['club'] = current_club
        context['page_obj'] = page_obj
        return context

@login_required
def meetings_list(request, club_id):
    club = Club.objects.get(id=club_id)
    meetings = club.get_meetings()
    paginator = Paginator(meetings, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'club_meetings.html', {'club': club, 'page_obj': page_obj})



class MeetingScheduler(LoginRequiredMixin, View):
    """View that handles meeting scheduling."""

    http_method_names = ['get', 'post']

    def get(self, request, pk):
        """Display meeting scheduler template"""
        return self.render(pk)

    def post(self, request, pk):
        """Handle scheduling attempt."""

        current_club=Club.objects.get(pk=pk)
        form = ScheduleMeetingForm(club=current_club, data=request.POST)
        if form.is_valid():
            meeting = form.save(club=current_club)
            messages.add_message(request, messages.SUCCESS, "The meeting was scheduled!")
            return redirect('home')
        messages.add_message(request, messages.ERROR, "The meeting was unable to be scheduled!")
        return self.render(pk)

    def render(self, pk):
        """Render meeting scheduler form"""
        current_club=Club.objects.get(pk=pk)
        form = ScheduleMeetingForm(club=current_club)
        return render(self.request, 'schedule_meeting.html', {'form': form, 'pk':pk})

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
            Meeting.objects.filter(id=meeting_id).delete()
            form.save(club)
            return redirect(reverse('club_meetings',kwargs={'club_id':club_id}))
        return render(request, 'edit_meeting.html', {"club": club, "form": form})

    def get(self, request, club_id, meeting_id, *args, **kwargs):
        club = Club.objects.get(id=club_id)
        meeting = Meeting.objects.get(id=meeting_id)
        form = self.form_class(instance=meeting, club=club)
        return render(request, 'edit_meeting.html', {"club": club,"form": form})