from django.conf import settings
from django.shortcuts import redirect
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from bookclub.models import User, Club, Post, Meeting
from bookclub.tests.helpers import LogInTester, reverse_with_next
from datetime import timedelta, date, time, datetime

"""Tests for Club Profile """


class ClubProfileTest(TestCase, LogInTester):
    fixtures = ['bookclub/tests/fixtures/default_users.json',
                'bookclub/tests/fixtures/default_clubs.json',
                'bookclub/tests/fixtures/default_applications.json',
                'bookclub/tests/fixtures/default_posts.json']

    def setUp(self):
        self.john = User.objects.get(pk=1)
        self.jane = User.objects.get(pk=2)
        self.joe = User.objects.get(pk=3)
        self.sam = User.objects.get(pk=4)
        self.bush_club = Club.objects.get(pk=1)
        self.somerset_club = Club.objects.get(pk=2)
        self.temple_club = Club.objects.get(pk=4)
        self.bush_club.make_member(self.jane)
        self.url = reverse('club_profile', kwargs={'club_id': self.bush_club.id})
        self.post_bush_club = Post.objects.get(pk=1)
        self.post_strand_club = Post.objects.get(pk=2)

    def test_club_profile_url(self):
        self.assertEqual(self.url, f'/club_profile/{self.bush_club.id}/')

    def test_correct_club_profile_template(self):
        self.client.login(email=self.john.email, password="Password123")
        response = self.client.get(self.url)
        self._is_logged_in()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_profile.html")

    def test_correct_club_profile_redirects_with_error_message_when_given_id_to_a_club_which_does_not_exist(self):
        self.client.login(email=self.john.email, password="Password123")
        url = reverse('club_profile', kwargs={'club_id': 500})
        redirect_url = reverse('club_list')
        response = self.client.get(url, follow=True)

        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

        my_messages = list(response.context['messages'])
        self.assertEqual(len(my_messages), 1)
        self.assertEqual(my_messages[0].level, messages.ERROR)
        self.assertEqual(my_messages[0].message, "Club does not exist!")

    def test_get_club_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_club_profile_has_correct_details(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('<img src=', html)
        self.assertIn(f' alt="Gravatar of {self.bush_club.name}" class="profile-image" style="border-radius: 10px">', html)
        self.assertIn(f'<h3>{self.bush_club.name}</h3>', html)
        self.assertIn(f'<p>{self.bush_club.description}</p>', html)
        self.assertIn(f'<a href="/user_profile/{self.bush_club.owner.id}/" style="text-decoration: none;">', html)
        self.assertIn(f'<h6 class="card-title">{self.bush_club.owner.first_name} {self.bush_club.owner.last_name}</h6>',
                      html)
        self.assertIn(f'</a>', html)
        self.assertIn(f'<h6 class="card-title">{self.bush_club.location}</h6>', html)

    def test_club_profile_view_has_cards(self):
        """Checks for card-specific (NOT club-specific) details in the club profile template."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('<div class="card w-100">', html)
        self.assertIn('<div class="card-body">', html)
        self.assertIn('<h6 class="card-title">', html)

    def test_club_profile_view_has_apply_button_for_non_member(self):
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(
            f'<button type="submit" class="btn" id="apply-button" style=\'padding: 10px;color:white; '
            f'background-color: brown; text-transform:uppercase; font-size: 14px\'><i class="bi bi-check-square"></i> '
            f'Apply</button>',
            html)

    def test_club_profile_view_has_meetings_list_button_for_owner(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a href="/club_profile/1/meetings" style="text-decoration: none;">View All</a>', html)

    def test_club_profile_view_has_meetings_list_button_for_organiser(self):
        self.bush_club.make_organiser(self.jane)
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a href="/club_profile/1/meetings" style="text-decoration: none;">View All</a>', html)

    def test_club_profile_view_has_meetings_list_button_for_member(self):
        self.bush_club.make_member(self.joe)
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a href="/club_profile/1/meetings" style="text-decoration: none;">View All</a>', html)

    """ Test if the club profile page doesn't have a leave button for a non-member of the club """

    def test_club_profile_view_doesnt_have_a_leave_button_for_non_member(self):
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertNotIn(
            f'<button type="submit" class="btn btn-default" id="leave-button"><span class="btn btn-dark" '
            f'style="background-color: brown;">Leave {self.bush_club.name}</button>',
            html)

    """Test if the club profile page has a leave button for a member of the club """

    def test_club_profile_view_has_a_leave_button_for_club_member(self):
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn btn-default" id="leave-button" style=\'padding: '
                      f'10px;color:white; background-color: brown; text-transform:uppercase; font-size: 14px\'><i '
                      f'class="bi bi-box-arrow-left"></i> Leave</button>', html)

    """Test if the club profile page has a leave button for a organiser of a club """

    def test_club_profile_view_has_a_leave_button_for_club_organiser(self):
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        self.bush_club.make_organiser(self.user3)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn btn-default" id="leave-button" style=\'padding: '
                      f'10px;color:white; background-color: brown; text-transform:uppercase; font-size: 14px\'><i '
                      f'class="bi bi-box-arrow-left"></i> Leave</button>', html)

    def test_disband_button_visible_for_owner(self):
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        self.bush_club.make_owner(self.user3)
        response = self.client.get(self.url)

        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn" id="leave-button" style=\'padding: 10px;color:white; '
                      f'background-color: brown; text-transform:uppercase; font-size: 14px\'><i class="bi '
                      f'bi-x-octagon"></i> Disband</button>', html)

    def test_disband_button_not_visible_for_member(self):
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        self.assertNotIn(f'<button type="submit" class="btn" id="leave-button" style=\'padding: 10px;color:white; '
                         f'background-color: brown; text-transform:uppercase; font-size: 14px\'><i class="bi '
                         f'bi-x-octagon"></i> Disband</button>', html)
        self.assertNotIn('Disband', html)

    def test_disband_button_not_visible_for_organiser(self):
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        self.bush_club.make_organiser(self.user3)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        self.assertNotIn(f'<button type="submit" class="btn btn-default" id="leave-button"><span class="btn btn-dark" '
                         f'style="background-color: brown;">Disband {self.bush_club.name}</button>', html)
        self.assertNotIn('Disband', html)

    def test_successful_disband(self):
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        self.bush_club.make_owner(self.user3)
        club_id = self.bush_club.id
        response = self.client.get(self.url + 'disband', follow=True)

        redirect_url = reverse('club_selector')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

        my_messages = list(response.context['messages'])
        self.assertEqual(len(my_messages), 1)
        self.assertEqual(my_messages[0].level, messages.SUCCESS)
        self.assertEqual(my_messages[0].message, f'{self.bush_club.name} has been disbanded!')
        self.assertFalse(Club.objects.filter(pk=club_id).exists())

    def test_club_profile_view_doesnt_have_a_post_button_for_non_member(self):
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertNotIn(f'<button type="submit" class="btn btn-default" id="post-feed"><span class="btn btn-dark" '
                         f'style="background-color: brown;">Club feed</button>', html)

    def test_club_profile_owner_has_a_post_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="button" class="btn float-end" data-bs-toggle="modal" '
                      f'data-bs-target="#staticBackdrop" style=\'padding-top: 10px; padding-bottom: 10px; '
                      f'color:white; background-color: brown; text-transform:uppercase; font-size: 14px\'>\n          '
                      f'                  <i class="bi bi-chat-square-text"></i> New Post', html)

    def test_club_owner_can_see_edit_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f' <a class="btn float-end" style=\'padding: 10px;color:white; margin-bottom: 20px; '
                      f'background-color: brown; text-transform:uppercase; font-size: 14px\' '
                      f'href="/club_profile/1/edit/"><i class="bi bi-pencil-square"></i> Edit Club</a>', html)

    def test_club_organiser_cannot_see_edit_button(self):
        self.bush_club.make_organiser(self.jane)
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertNotIn(f' <a class="btn float-end" style=\'padding: 10px;color:white; margin-bottom: 20px; '
                         f'background-color: brown; text-transform:uppercase; font-size: 14px\' '
                         f'href="/club_profile/1/edit/"><i class="bi bi-pencil-square"></i> Edit Club</a>', html)

    def test_club_member_cannot_see_edit_button(self):
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertNotIn(f' <a class="btn float-end" style=\'padding: 10px;color:white; margin-bottom: 20px; '
                         f'background-color: brown; text-transform:uppercase; font-size: 14px\' '
                         f'href="/club_profile/1/edit/"><i class="bi bi-pencil-square"></i> Edit Club</a>', html)

    def test_club_profile_view_has_feed_view_button_for_owner(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a href="/club_profile/1/feed/" style="text-decoration: none;">View All</a>', html)

    def test_club_profile_view_has_feed_view_button_for_organiser(self):
        self.bush_club.make_organiser(self.jane)
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a href="/club_profile/1/feed/" style="text-decoration: none;">View All</a>', html)

    def test_club_profile_view_has_feed_view_button_for_member(self):
        self.bush_club.make_member(self.joe)
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a href="/club_profile/1/feed/" style="text-decoration: none;">View All</a>', html)

    """Test the owner-organiser privilege mechanism"""

    def test_club_profile_view_when_owner_organiser_true_post_button(self):
        self.somerset_club.make_member(self.sam)
        self.somerset_club.make_organiser(self.sam)
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.somerset_club.id}))
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="button" class="btn float-end" data-bs-toggle="modal" '
                      f'data-bs-target="#staticBackdrop" style=\'padding-top: 10px; padding-bottom: 10px; '
                      f'color:white; background-color: brown; text-transform:uppercase; font-size: 14px\'>\n          '
                      f'                  <i class="bi bi-chat-square-text"></i> New Post', html)

    def test_club_profile_view_when_owner_organiser_false_post_button(self):
        self.bush_club.make_member(self.sam)
        self.bush_club.make_organiser(self.sam)
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.bush_club.id}))
        html = response.content.decode('utf8')
        self.assertNotIn(f'<button type="button" class="btn float-end" data-bs-toggle="modal" '
                         f'data-bs-target="#staticBackdrop" style=\'padding-top: 10px; padding-bottom: 10px; '
                         f'color:white; background-color: brown; text-transform:uppercase; font-size: 14px\'>\n '
                         f'                  <i class="bi bi-chat-square-text"></i> New Post', html)

    def test_club_profile_view_when_owner_organiser_true_schedule_button(self):
        self.somerset_club.make_member(self.sam)
        self.somerset_club.make_organiser(self.sam)
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.somerset_club.id}))
        html = response.content.decode('utf8')
        self.assertIn(f'<a class="btn float-end" href="/club_profile/2/meeting/" style="padding-top: 10px; '
                      f'padding-bottom: 10px; color:white; background-color: brown; text-transform:uppercase; '
                      f'font-size: 14px"><i class="bi bi-calendar-plus"></i> Schedule Meeting</a>', html)

    def test_club_profile_view_when_owner_organiser_false_schedule_button(self):
        self.bush_club.make_member(self.sam)
        self.bush_club.make_organiser(self.sam)
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.bush_club.id}))
        html = response.content.decode('utf8')
        self.assertNotIn(f'<a class="btn float-end" href="/club_profile/2/meeting/" style="padding-top: 10px; '
                         f'padding-bottom: 10px; color:white; background-color: brown; text-transform:uppercase; '
                         f'font-size: 14px"><i class="bi bi-calendar-plus"></i> Schedule Meeting</a>', html)

    """ Test to check whether some posts and meetings appear on club profile page """

    def test_club_profile_view_has_posts(self):
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.bush_club.id}))
        html = response.content.decode('utf8')
        self.assertIn(f' <p class="card-text fw-bold">This is a Bush House Book Club Post</p>',
                      html)

    def test_club_profile_view_does_not_display_other_club_posts(self):
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.somerset_club.id}))
        html = response.content.decode('utf8')
        self.assertNotIn(f' <p class="card-text fw-bold">This is a Bush House Book Club Post</p>',
                         html)

    def test_club_profile_view_displays_correct_message_when_no_posts(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.temple_club.id}))
        html = response.content.decode('utf8')
        self.assertIn(f'<p class="text-muted"><strong>{self.temple_club.name}</strong> does not have any posts</p>',
                      html)

    def test_club_profile_view_has_meeting(self):
        self.today = date.today()
        next_hour_date_time = datetime.now() + timedelta(hours=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.future_time = time(next_hour_date_time.hour, 0)
        self.meeting = Meeting.objects.create(start_time=self.future_time, date=self.tomorrow, club=self.bush_club, address='www.google.com')
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.bush_club.id}))
        html = response.content.decode('utf8')
        self.assertIn(f'<h6 class="card-title">www.google.com</h6>', html)

    def test_club_profile_view_does_not_display_other_club_meetings(self):
        self.today = date.today()
        next_hour_date_time = datetime.now() + timedelta(hours=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.future_time = time(next_hour_date_time.hour, 0)
        self.meeting = Meeting.objects.create(start_time=self.future_time, date=self.tomorrow, club=self.bush_club, address='www.google.com')
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.temple_club.id}))
        html = response.content.decode('utf8')
        self.assertNotIn(f'<h6 class="card-title">www.google.com</h6>', html)

    def test_club_profile_view_displays_correct_message_when_no_meetings(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.temple_club.id}))
        html = response.content.decode('utf8')
        self.assertIn(f'<p class="text-muted"><strong>{self.temple_club.name}</strong> does not have any meetings</p>',
                      html)

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()
