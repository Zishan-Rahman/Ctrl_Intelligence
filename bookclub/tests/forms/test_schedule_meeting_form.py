"""Unit tests for the Schedule Meetings Form"""
from django.test import TestCase
from bookclub.forms import ScheduleMeetingForm
from django import forms
from bookclub.models import Club, User, Meeting
from datetime import timedelta, date, time, datetime


class TestScheduleMeeting(TestCase):
    """Test case for the Schedule Meetings Form"""
    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.john =  User.objects.get(pk=1)
        self.bush_club = Club.objects.get(pk=1)
        self.strand_club = Club.objects.get(pk=3)
        self.today = date.today()
        self.client.login(email=self.john.get_email(), password='Password123')
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)
        last_hour_date_time = datetime.now() - timedelta(minutes=1)
        next_hour_date_time = datetime.now() + timedelta(hours=1)
        self.past_time = time(last_hour_date_time.hour, 0)
        self.future_time = time(next_hour_date_time.hour, 0)

        self.online_form_input = {
            'date':self.tomorrow,
            'start_time':self.future_time,
            'address':'https://www.teams.com/thismeeting'
        }
        self.in_person_form_input = {
            'date':self.tomorrow,
            'start_time':self.future_time,
            'address':'123 Road London'
        }
    def test_online_schedule_meeting_form_has_necessary_fields(self):
        """Tests if online schedule meeting form has necessary fields."""
        form = ScheduleMeetingForm(club=self.bush_club)
        self.assertIn('date', form.fields)
        self.assertIn('start_time', form.fields)
        self.assertIn('address', form.fields)

    def test_in_person_schedule_meeting_form_has_necessary_fields(self):
        """Tests if in-person schedule meeting form has necessary fields."""
        form = ScheduleMeetingForm(club=self.strand_club)
        self.assertIn('date', form.fields)
        self.assertIn('start_time', form.fields)
        self.assertIn('address', form.fields)

    def test_valid_online_schedule_meeting_form(self):
        """Testing for valid online schedule meeting form."""
        form = ScheduleMeetingForm(data=self.online_form_input, club=self.bush_club)
        self.assertTrue(form.is_valid())

    def test_valid_in_person_schedule_meeting_form(self):
        """Testing for valid if in-person schedule meeting."""
        form = ScheduleMeetingForm(data=self.in_person_form_input, club=self.strand_club)
        self.assertTrue(form.is_valid())

    def test_form_accepts_valid_date_time(self):
        """Tests if schedule meeting form accepts valid date and time."""
        form = ScheduleMeetingForm(data=self.online_form_input, club=self.bush_club)
        self.assertTrue(form.is_valid())

    def test_form_rejects_past_date(self):
        """Tests if schedule meeting form rejects a date in the past."""
        self.online_form_input['date'] = self.yesterday
        form = ScheduleMeetingForm(data=self.online_form_input, club=self.bush_club)
        self.assertFalse(form.is_valid())

    def test_form_rejects_current_date_past_time(self):
        """Tests if schedule meeting form is rejects a time in the past."""
        self.online_form_input['date'] = self.today
        self.online_form_input['start_time'] = self.past_time
        form = ScheduleMeetingForm(data=self.online_form_input ,club=self.bush_club)
        self.assertFalse(form.is_valid())
