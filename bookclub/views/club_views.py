from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import ListView
from bookclub.models import Club
from bookclub.views import config
from django.urls import reverse
from django.contrib import messages
from bookclub.templates import *
from bookclub.forms import EditClubForm, PostForm, ClubForm, ScheduleMeetingForm
from django.http import Http404
from bookclub.models import User, Club, Post, Meeting, Application
from django.views.generic.edit import UpdateView
from django.core.paginator import Paginator



class ClubMemberListView(LoginRequiredMixin, ListView):
    """Gets the members of each club"""

    model = Club
    template_name = "club_members.html"
    pk_url_kwarg = 'club_id'
    context_object_name = 'club'
    ordering = ['-name']
    paginate_by = settings.USERS_PER_PAGE

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to book_list if book_id invalid."""
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('home')

    def get_queryset(self):
        return Club.objects.get(id=self.kwargs['club_id']).get_all_users()

    def get_context_data(self, *args, **kwargs):
        current_user_is_owner = False
        context = super().get_context_data(*args, **kwargs)
        current_club_id = self.kwargs['club_id']
        current_club = Club.objects.get(id=current_club_id)
        all_users = current_club.get_all_users()
        current_club = Club.objects.get(id=current_club_id)
        if current_club.owner == self.request.user:
            current_user_is_owner = True
        paginator = Paginator(current_club.get_all_users(), settings.USERS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        for each in page_obj:
            u_id = each.pk
            if current_club.user_level(each) == "Member":
                user_level = "Member"
                u_id = each.pk
            elif current_club.user_level(each) == "Organiser":
                user_level = "Organiser"
                u_id = each.pk
            else:
                user_level = "Owner"
                u_id = each.pk
                if each == self.request.user:
                    current_user_is_owner = True

        context['u_pk'] = u_id
        context['club'] = current_club
        context['all_users'] = all_users
        context['page_obj'] = page_obj
        context['user_level'] = user_level
        context['c_pk'] = current_club_id
        context['is_owner'] = current_user_is_owner
        context['current_user'] = self.request.user
        return context


@login_required
def promote_member_to_organiser(request, c_pk, u_pk):
    """Promote member to organiser"""
    try:
        club = Club.objects.all().get(pk=c_pk)
        if request.user == club.owner:
            user = User.objects.all().get(pk=u_pk)
            if user in club.get_organisers():
                messages.add_message(request, messages.ERROR, "This person is already an organiser!")
            else:
                new_organiser = User.objects.all().get(pk=u_pk)
                club.make_organiser(new_organiser)
                messages.add_message(request, messages.SUCCESS, str(new_organiser.get_full_name()) + " has been promoted!")
        else:
            messages.add_message(request, messages.ERROR, "You do not have authority to do this!")
        return redirect('club_members', club_id=c_pk)
    except (User.DoesNotExist, Club.DoesNotExist):
        messages.add_message(request, messages.ERROR, "Too many inputs")
        return redirect('club_members', club_id=c_pk)


@login_required
def demote_organiser_to_member(request, c_pk, u_pk):
    """Demote organiser to member"""
    try:
        club = Club.objects.all().get(pk=c_pk)
        if request.user == club.owner:
            new_member = User.objects.all().get(pk=u_pk)
            club.demote_organiser(new_member)
            messages.add_message(request, messages.ERROR, str(new_member.get_full_name()) + " has been demoted!")
        else:
            messages.add_message(request, messages.ERROR, "You do not have authority to do this!")
        return redirect('club_members', club_id=c_pk)
    except (User.DoesNotExist, Club.DoesNotExist):
        messages.add_message(request, messages.ERROR, "Too many inputs")
        return redirect('club_members', club_id=c_pk)


@login_required
def kick_user_from_club(request, c_pk, u_pk):
    """Promote member to organiser"""
    try:
        club = Club.objects.all().get(pk=c_pk)
        if request.user == club.owner:
            user_to_kick = User.objects.all().get(pk=u_pk)
            club.remove_from_club(user_to_kick)
            messages.add_message(request, messages.ERROR, str(user_to_kick.get_full_name()) + " has been kicked out!")
        else:
            messages.add_message(request, messages.ERROR, "You do not have authority to do this!")
        return redirect('club_members', club_id=c_pk)
    except (User.DoesNotExist, Club.DoesNotExist):
        messages.add_message(request, messages.ERROR, "Too many inputs")
        return redirect('club_members', club_id=c_pk)

@login_required
def transfer_ownership(request, c_pk, u_pk):
    """Transfer ownership to specific member"""
    try:
        club = Club.objects.get(pk=c_pk)
        if request.user == club.owner:
            new_owner = User.objects.get(pk=u_pk)
            club.make_owner(new_owner)
            messages.add_message(request, messages.SUCCESS,
                                "Transferred Ownership to " + str(new_owner.get_full_name()) + "!")
        else:
            messages.add_message(request, messages.ERROR, "You do not have authority to do this!")
        return redirect('club_members', club_id=c_pk)
    except (User.DoesNotExist, Club.DoesNotExist):
        messages.add_message(request, messages.ERROR, "Too many inputs")
        return redirect('club_members', club_id=c_pk)



class ClubUpdateView(LoginRequiredMixin, UpdateView):
    """View to update club profile."""

    model = EditClubForm
    template_name = "edit_club.html"
    form_class = EditClubForm

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Club updated!")
        return reverse('club_profile', kwargs={'club_id': self.pk})

    def post(self, request, c_pk, *args, **kwargs):
        self.pk = c_pk
        club_to_edit = Club.objects.all().get(pk=c_pk)
        form = self.form_class(instance=club_to_edit, data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return render(request, 'edit_club.html', {"form": form})

    def get(self, request, c_pk, *args, **kwargs):
        self.pk = c_pk
        club_to_edit = Club.objects.all().get(pk=c_pk)
        if request.user == club_to_edit.owner:
            form = self.form_class(instance=club_to_edit)
            return render(request, 'edit_club.html', {"form": form})
        else:
            messages.add_message(self.request, messages.ERROR, "Action prohibited")
            return redirect('club_list')


def club_util(request):
    user_clubs_list = []
    clubs = Club.objects.all()

    for temp_club in clubs:
        if request.user in temp_club.get_all_users():
            user_clubs_list.append(temp_club)

    config.user_clubs = user_clubs_list

@login_required
def club_selector(request):
    club_util(request)
    return render(request, "club_switcher.html", {'user_clubs': config.user_clubs, 'user': request.user})


@login_required
def club_selector_alt(request):
    club_util(request)
    return render(request, "club_switcher_alt.html", {"user_clubs": config.user_clubs, 'user': request.user})


@login_required
def new_club(request):  # new club adapted from the chess club project
    """ Create New Club """
    if request.method == 'POST':
        form = ClubForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            club_util(request)
            messages.add_message(request, messages.SUCCESS, "Club has been created!")
            return redirect('club_selector')
    else:
        form = ClubForm()
    return render(request, 'new_club.html', {'form': form})


class ClubsListView(LoginRequiredMixin, ListView):
    """View that shows a list of all clubs."""

    model = Club
    template_name = "club_list.html"
    context_object_name = "clubs"
    queryset = Club.objects.all()
    paginate_by = settings.CLUBS_PER_PAGE


@login_required
def club_profile(request, club_id):
    """ Individual Club's Profile Page """
    try:
        club = Club.objects.get(id=club_id)
        edit_club_form = EditClubForm()
        post_form = PostForm()
        posts = Post.objects.filter(club=club)
        posts = posts[:6]
        meeting_form = ScheduleMeetingForm(club=club)
        meetings = Meeting.objects.filter(club=club)
        meetings = meetings[:3]
        applied_to = Application.objects.filter(applicant=request.user)
        applied_to_list = []
        for x in applied_to:
            applied_to_list.append(x.club)
    except:
        messages.add_message(request, messages.ERROR, "Club does not exist!")
        return redirect('club_list')

    current_user = request.user
    is_owner = club.user_level(current_user) == "Owner"
    
    return render(request, 'club_profile.html', {
        'club': club,
        'current_user': current_user,
        'is_owner': is_owner,
        'posts': posts,
        'meetings': meetings,
        'post_form': post_form,
        'meeting_form': meeting_form,
        'edit_club_form': edit_club_form,
        'applied_to': applied_to_list
        }
    )


@login_required
def leave_club(request, club_id):
    """Leave A Club """
    club = Club.objects.get(pk=club_id)
    current_user = request.user
    club.remove_from_club(current_user)
    messages.add_message(request, messages.SUCCESS, f"You have successfully left {club.name}!")
    return redirect('club_selector')

@login_required
def disband_club(request, c_pk):
    """Disband a club"""
    club = Club.objects.get(pk=c_pk)
    club.delete()
    messages.add_message(request, messages.SUCCESS, f"{club.name} has been disbanded!")
    return redirect('club_selector')
