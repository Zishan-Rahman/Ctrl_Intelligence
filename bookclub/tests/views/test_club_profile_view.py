"""Unit tests for the Club Profile View"""
from django.conf import settings
from django.shortcuts import redirect
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from bookclub.models import User, Club, Post, Meeting, Application
from bookclub.tests.helpers import LogInTester, reverse_with_next
from datetime import timedelta, date, time, datetime


class ClubProfileTest(TestCase, LogInTester):
    """Test case for the Club Profile view"""
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
        """Testing the club profile url."""
        self.assertEqual(self.url, f'/club_profile/{self.bush_club.id}/')

    def test_correct_club_profile_template(self):
        """Testing if the club profile uses correct template."""
        self.client.login(email=self.john.email, password="Password123")
        response = self.client.get(self.url)
        self._is_logged_in()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_profile.html")

    def test_correct_club_profile_redirects_with_error_message_when_given_id_to_a_club_which_does_not_exist(self):
        """Test if club is inexistent, redirect to club list."""
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
        """Test if not logged in, redirect to club profile."""
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_club_profile_has_correct_details(self):
        """Testing if club profile has the correct details."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'alt="Gravatar of {self.bush_club.name}', html)
        self.assertIn(f'{self.bush_club.name}', html)
        self.assertIn(f'{self.bush_club.description}', html)
        self.assertIn(f'{self.bush_club.owner.id}', html)
        self.assertIn(f'{self.bush_club.owner.first_name} {self.bush_club.owner.last_name}',
                      html)
        self.assertIn(f'{self.bush_club.location}', html)

    def test_club_profile_view_has_apply_button_for_non_member(self):
        """Testing for apply button on club profile for non members."""
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('<button type="submit" class="btn w-50 mx-auto" aria-disabled="true" style="padding: 15px; color: white; background-color: #353535; text-transform:uppercase; font-size: 14px"><i class="bi bi-check-square"></i> Applied</button>', html)

    def test_club_profile_view_can_successfully_apply_for_non_member(self):
        self.client.login(email=self.joe.email, password='Password123')
        before_application_count = Application.objects.filter(club=self.temple_club).count()
        response = self.client.post(f'/new_application/{self.temple_club.id}/', follow=True)
        self.temple_club.refresh_from_db()
        redirect_url = f'/my_applications/'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        after_application_count = Application.objects.filter(club=self.temple_club).count()
        self.assertNotEqual(before_application_count, after_application_count)

    def test_club_profile_view_can_unsuccessfully_apply_for_member(self):
        self.client.login(email=self.joe.email, password='Password123')
        self.temple_club.make_member(self.joe)
        before_application_count = Application.objects.filter(club=self.temple_club).count()
        response = self.client.post(f'/new_application/{self.temple_club.id}/', follow=True)
        self.temple_club.refresh_from_db()
        redirect_url = f'/my_applications/'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_application_count = Application.objects.filter(club=self.temple_club).count()
        self.assertEqual(before_application_count, after_application_count)


    def test_club_profile_view_has_meetings_list_button_for_owner(self):
        """Testing if owner has meetings list button on club profile."""
        self.today = date.today()
        next_hour_date_time = datetime.now() + timedelta(hours=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.future_time = time(next_hour_date_time.hour, 0)
        self.meeting = Meeting.objects.create(start_time=self.future_time, date=self.tomorrow, club=self.bush_club, address='www.google.com')
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a href="/club_profile/1/meetings" style="text-decoration: none;">View All</a>', html)

    def test_club_profile_view_has_meetings_list_button_for_organiser(self):
        """Testing if organiser has meetings list button on club profile."""
        self.today = date.today()
        next_hour_date_time = datetime.now() + timedelta(hours=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.future_time = time(next_hour_date_time.hour, 0)
        self.meeting = Meeting.objects.create(start_time=self.future_time, date=self.tomorrow, club=self.bush_club,
                                              address='www.google.com')
        self.bush_club.make_organiser(self.jane)
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a href="/club_profile/1/meetings" style="text-decoration: none;">View All</a>', html)

    def test_club_profile_view_has_meetings_list_button_for_member(self):
        """Testing if member has meetings list button on club profile."""
        self.today = date.today()
        next_hour_date_time = datetime.now() + timedelta(hours=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.future_time = time(next_hour_date_time.hour, 0)
        self.meeting = Meeting.objects.create(start_time=self.future_time, date=self.tomorrow, club=self.bush_club,
                                              address='www.google.com')
        self.bush_club.make_member(self.joe)
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a href="/club_profile/1/meetings" style="text-decoration: none;">View All</a>', html)

    def test_club_profile_view_doesnt_have_a_leave_button_for_non_member(self):
        """ Test if the club profile page doesn't have a leave button for a non-member of the club."""
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertNotIn('<button type="submit" class="btn" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#leaveClub" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-box-arrow-left"></i> Leave</button>', html)

    def test_club_profile_view_has_a_leave_button_for_club_member(self):
        """Test if the club profile page has a leave button for a member of the club."""
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('<button type="submit" class="btn" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#leaveClub" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-box-arrow-left"></i> Leave</button>', html)

    def test_club_profile_view_has_a_leave_button_for_club_organiser(self):
        """Test if the club profile page has a leave button for an organiser of a club."""
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        self.bush_club.make_organiser(self.user3)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('<button type="submit" class="btn" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#leaveClub" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-box-arrow-left"></i> Leave</button>', html)

    def test_disband_button_visible_for_owner(self):
        """Test if disband button is visible for owner on club profile page."""
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        self.bush_club.make_owner(self.user3)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('<button type="submit" class="btn" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#disbandClub" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-x-octagon"></i> Disband</button>', html)

    def test_disband_button_not_visible_for_member(self):
        """Test if disband button is invisible for member."""
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertNotIn('<button type="submit" class="btn" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#disbandClub" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-x-octagon"></i> Disband</button>', html)

    def test_disband_button_not_visible_for_organiser(self):
        """Test if disband button is invisible for an organiser."""
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        self.bush_club.make_organiser(self.user3)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertNotIn('<button type="submit" class="btn" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#disbandClub" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-x-octagon"></i> Disband</button>', html)

    def test_successful_disband(self):
        """Test for successful disband of a club."""
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
        """Test if post button is not on club profile for non member."""
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertNotIn('<button type="button" class="btn float-end" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#newPost" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-chat-square-text"></i> New Post</button>', html)

    def test_club_profile_owner_has_a_post_button(self):
        """Test if post button is on club profile for club owner."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('<button type="button" class="btn float-end" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#newPost" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-chat-square-text"></i> New Post</button>', html)

    def test_club_owner_can_see_edit_button(self):
        """Test if edit button is on club profile for club owner."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('<button class="btn float-end mb-3" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#editClub" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-pencil-square"></i> Edit Club</button>', html)

    def test_club_organiser_cannot_see_edit_button(self):
        """Test if edit button is not on club profile for organiser."""
        self.bush_club.make_organiser(self.jane)
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertNotIn('<button class="btn float-end mb-3" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#editClub" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-pencil-square"></i> Edit Club</button>', html)

    def test_club_member_cannot_see_edit_button(self):
        """Test if edit button is not on club profile for member."""
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertNotIn('<button class="btn float-end mb-3" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#editClub" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-pencil-square"></i> Edit Club</button>', html)

    def test_club_profile_view_has_feed_view_button_for_owner(self):
        """Test if feed view button is on club profile for owner."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a href="/club_profile/1/feed/" style="text-decoration: none;">View All</a>', html)

    def test_club_profile_view_has_feed_view_button_for_organiser(self):
        """Test if feed view button is on club profile for organiser."""
        self.bush_club.make_organiser(self.jane)
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a href="/club_profile/1/feed/" style="text-decoration: none;">View All</a>', html)

    def test_club_profile_view_has_feed_view_button_for_member(self):
        """Test if feed view button is on club profile for member."""
        self.bush_club.make_member(self.joe)
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a href="/club_profile/1/feed/" style="text-decoration: none;">View All</a>', html)

    """Test the owner-organiser privilege mechanism"""

    def test_club_profile_view_when_owner_organiser_true_post_button(self):
        """Test for true post button on club profile for owner and organiser."""
        self.somerset_club.make_member(self.sam)
        self.somerset_club.make_organiser(self.sam)
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.somerset_club.id}))
        html = response.content.decode('utf8')
        self.assertIn(f'New Post', html)

    def test_club_profile_view_when_owner_organiser_false_post_button(self):
        """Test for false post button on club profile for owner and organiser."""
        self.bush_club.make_member(self.sam)
        self.bush_club.make_organiser(self.sam)
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.bush_club.id}))
        html = response.content.decode('utf8')
        self.assertNotIn('<button type="button" class="btn float-end" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#newPost" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-chat-square-text"></i> New Post</button>', html)

    def test_club_profile_view_when_owner_organiser_true_schedule_button(self):
        """Test for true schedule button on club profile for owner and organiser."""
        self.somerset_club.make_member(self.sam)
        self.somerset_club.make_organiser(self.sam)
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.somerset_club.id}))
        html = response.content.decode('utf8')
        self.assertIn('<button type="submit" class="btn float-end" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#scheduleMeeting" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-calendar-plus"></i> Schedule Meeting</button>', html)

    def test_club_profile_view_when_owner_organiser_false_schedule_button(self):
        """Test for false schedule button on club profile for owner and organiser."""
        self.bush_club.make_member(self.sam)
        self.bush_club.make_organiser(self.sam)
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.bush_club.id}))
        html = response.content.decode('utf8')
        self.assertNotIn('<button type="submit" class="btn float-end" id="bookwiseGeneralBtn" data-bs-toggle="modal" data-bs-target="#scheduleMeeting" style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-calendar-plus"></i> Schedule Meeting</button>', html)

    """ Test to check whether some posts and meetings appear on club profile page """

    def test_club_profile_view_has_posts(self):
        """Test if club profile shows posts."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.bush_club.id}))
        html = response.content.decode('utf8')
        self.assertIn(f'This is a Bush House Book Club Post', html)

    def test_club_profile_view_does_not_display_other_club_posts(self):
        """Test if club profile does not show posts from other clubs."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.somerset_club.id}))
        html = response.content.decode('utf8')
        self.assertNotIn(f'This is a Bush House Book Club Post', html)

    def test_club_profile_view_displays_correct_message_when_no_posts(self):
        """Test for correct message when club profile does contain any posts."""
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.temple_club.id}))
        html = response.content.decode('utf8')
        self.assertIn(f'<p class="text-muted"><strong>{self.temple_club.name}</strong> does not have any posts</p>', html)

    def test_club_profile_view_has_meeting(self):
        """Test if club profile has meeting feature."""
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
        """Test if club profile does not show meetings from other clubs."""
        self.today = date.today()
        next_hour_date_time = datetime.now() + timedelta(hours=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.future_time = time(next_hour_date_time.hour, 0)
        self.meeting = Meeting.objects.create(start_time=self.future_time, date=self.tomorrow, club=self.bush_club, address='www.google.com')
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.temple_club.id}))
        html = response.content.decode('utf8')
        self.assertNotIn(f'<h6 class="card-title">www.google.com</h6>', html)

    def test_club_profile_view_displays_correct_message_when_no_meetings(self):
        """Test for correct message on club profile when club does not have any meetings."""
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(reverse('club_profile', kwargs={'club_id': self.temple_club.id}))
        html = response.content.decode('utf8')
        self.assertIn(f'<p class="text-muted"><strong>{self.temple_club.name}</strong> does not have any meetings</p>', html)

    def test_successful_leave_club(self):
        """Test if a user is able to successfully leave a club"""
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        club_id = self.bush_club.id
        response = self.client.post(f'/leave_club/{club_id}/' , follow = True)
        redirect_url = reverse('club_selector')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        my_messages = list(response.context['messages'])
        self.assertEqual(len(my_messages), 1)
        self.assertEqual(my_messages[0].level, messages.SUCCESS)
        self.assertEqual(my_messages[0].message, f'You have successfully left {self.bush_club.name}!')

    def _is_logged_in(self):
        """Test if logged in."""
        return '_auth_user_id' in self.client.session.keys()
