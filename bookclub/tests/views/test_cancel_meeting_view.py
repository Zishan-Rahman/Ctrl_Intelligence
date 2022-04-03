"""Unit tests for the Cancel Meeting View"""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Meeting
from django.contrib import messages
from bookclub.forms import ScheduleMeetingForm
from bookclub.tests.helpers import LogInTester, reverse_with_next
from datetime import timedelta, date, time, datetime


class TestCancelMeetingView(TestCase, LogInTester):
    """Test case for the Cancel Meeting view"""
    fixtures = ['bookclub/tests/fixtures/default_users.json',
                'bookclub/tests/fixtures/default_clubs.json',
                ]

    def setUp(self):
        self.john = User.objects.get(pk=1)
        self.jane = User.objects.get(pk=2)
        self.joe = User.objects.get(pk=3)
        self.bush_club = Club.objects.get(pk=1)
        self.somerset_club = Club.objects.get(pk=2)
        self.temple_club = Club.objects.get(pk=4)
        self.bush_club.make_member(self.jane)
        self.somerset_club.make_member(self.john)
        self.somerset_club.make_organiser(self.john)
        self.bush_club.make_member(self.joe)
        self.bush_club.make_organiser(self.joe)


    def test_cancel_meeting_button_visible_for_owner(self):
        """"Test if cancel meeting button is visible to the owner of the club."""
        self.today = date.today()
        next_hour_date_time = datetime.now() + timedelta(hours=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.future_time = time(next_hour_date_time.hour, 0)
        self.meeting = Meeting.objects.create(start_time=self.future_time, date=self.tomorrow, club=self.bush_club,
                                              address='www.google.com')
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get('/club_profile/1/meetings')
        html = response.content.decode('utf8')
        self.assertIn(f'Cancel Meeting', html)

    def test_cancel_meeting_button_is_not_visible_for_member(self):
        """"Test if cancel meeting button is invisible to members"""
        self.today = date.today()
        next_hour_date_time = datetime.now() + timedelta(hours=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.future_time = time(next_hour_date_time.hour, 0)
        self.meeting = Meeting.objects.create(start_time=self.future_time, date=self.tomorrow, club=self.bush_club,
                                              address='www.google.com')
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get('/club_profile/1/meetings')
        html = response.content.decode('utf8')
        self.assertNotIn(f'Cancel Meeting', html)

    def test_cancel_meeting_button_is_visible_for_organisers_when_owner_organiser_true(self):
        """"Test if true, cancel meeting button is visible to organisers."""
        self.today = date.today()
        next_hour_date_time = datetime.now() + timedelta(hours=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.future_time = time(next_hour_date_time.hour, 0)
        self.meeting = Meeting.objects.create(start_time=self.future_time, date=self.tomorrow, club=self.somerset_club,
                                              address='www.google.com')
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get('/club_profile/2/meetings')
        html = response.content.decode('utf8')
        self.assertIn(f'Cancel Meeting', html)

    def test_cancel_meeting_button_is_not_visible_for_organisers_when_owner_organiser_false(self):
        """"Test if false, cancel meeting button is invisible to the organiser."""
        self.today = date.today()
        next_hour_date_time = datetime.now() + timedelta(hours=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.future_time = time(next_hour_date_time.hour, 0)
        self.meeting = Meeting.objects.create(start_time=self.future_time, date=self.tomorrow, club=self.bush_club,
                                              address='www.google.com')
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get('/club_profile/1/meetings')
        html = response.content.decode('utf8')
        self.assertNotIn(f'Cancel Meeting', html)

    def test_successful_cancel_meeting(self):
        """"Testing for a succesfully cancelled meeting."""
        self.today = date.today()
        next_hour_date_time = datetime.now() + timedelta(hours=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.future_time = time(next_hour_date_time.hour, 0)
        self.meeting = Meeting.objects.create(start_time=self.future_time, date=self.tomorrow, club=self.bush_club,
                                              address='www.google.com')
        self.client.login(email=self.john.email, password='Password123')
        beforeMeetingListCount = self.bush_club.get_number_of_meetings()
        response = self.client.get('/club_profile/1/meetings/1/delete', follow=True)
        redirect_url = '/club_profile/1/meetings'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        afterMeetingListCount = self.bush_club.get_number_of_meetings()
        self.assertEqual(beforeMeetingListCount, afterMeetingListCount + 1)

    def _is_logged_in(self):
        """"Testing if logged in."""
        return '_auth_user_id' in self.client.session.keys()
