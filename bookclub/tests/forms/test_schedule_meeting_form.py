"""Unit tests for the create meetings form."""
from django.test import TestCase
from bookclub.forms import ScheduleMeetingForm
from django import forms
from bookclub.models import Club, User, Meeting
from datetime import timedelta, date, time, datetime


class ScheduleMeetingTestCase(TestCase):

    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.john =  User.objects.get(pk=1)
        self.bush_club = Club.objects.get(pk=1)
        self.strand_club = Club.objects.get(pk=3)
        self.today = date.today()
        self.client.login(email=self.john.get_email(), password='Password123')
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)
        last_hour_date_time = datetime.now() - timedelta(hours = 1)
        next_hour_date_time = datetime.now() + timedelta(hours = 1)
        self.past_time = time(last_hour_date_time.hour, 0)
        self.future_time = time(next_hour_date_time.hour, 0)

        self.online_form_input = {
            'date':self.tomorrow,
            'time':self.future_time
        }
        self.in_person_form_input = {
            'date':self.tomorrow,
            'time':self.future_time,
            'meeting_address':'123 Road London'
        }

    def test_online_schedule_meeting_form_has_necessary_fields(self):
        form = ScheduleMeetingForm(club=self.bush_club)
        self.assertIn('date', form.fields)
        self.assertIn('time', form.fields)
        self.assertNotIn('meeting_address', form.fields)

    def test_in_person_schedule_meeting_form_has_necessary_fields(self):
        form = ScheduleMeetingForm(club=self.strand_club)
        self.assertIn('date', form.fields)
        self.assertIn('time', form.fields)
        self.assertIn('meeting_address', form.fields)

    def test_valid_online_schedule_meeting_form(self):
        form = ScheduleMeetingForm(data=self.online_form_input, club=self.bush_club)
        self.assertTrue(form.is_valid())
    
    def test_valid_in_person_schedule_meeting_form(self):
        form = ScheduleMeetingForm(data=self.in_person_form_input, club=self.strand_club)
        self.assertTrue(form.is_valid())

    def test_form_accepts_valid_date_time(self):
        form = ScheduleMeetingForm(data=self.online_form_input, club=self.bush_club)
        self.assertTrue(form.is_valid())

    def test_form_rejects_past_date(self):
        self.online_form_input['date'] = self.yesterday
        form = ScheduleMeetingForm(data=self.online_form_input, club=self.bush_club)
        self.assertFalse(form.is_valid())

    def test_form_rejects_current_date_past_time(self):
        self.online_form_input['date'] = self.today
        self.online_form_input['time'] = self.past_time
        form = ScheduleMeetingForm(data=self.online_form_input ,club=self.bush_club)
        self.assertFalse(form.is_valid())
