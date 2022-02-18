"""Unit tests for the create meetings form."""
from django.test import TestCase
from bookclub.forms import ScheduleMeetingForm
from django import forms
from bookclub.models import Club, User, Meeting
from datetime import timedelta, date, time, datetime


class CreateClubTestForm(TestCase):

    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.john =  User.objects.get(pk=1)
        self.bush_club = Club.objects.get(pk=1)
        self.today = date.today()
        self.client.login(email=self.john.get_email(), password='Password123')
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)
        last_hour_date_time = datetime.now() - timedelta(hours = 1)
        next_hour_date_time = datetime.now() + timedelta(hours = 1)
        self.past_time = time(last_hour_date_time.hour, 0)
        self.future_time = time(next_hour_date_time.hour, 0)

        self.form_input = {
            'date':self.tomorrow,
            'time':self.future_time
        }

    def test_schedule_meeting_form_has_necessary_fields(self):
        form = ScheduleMeetingForm(club=self.bush_club)
        self.assertIn('date', form.fields)
        self.assertIn('time', form.fields)

    def test_valid_schedule_meeting_form(self):
        form = ScheduleMeetingForm(club=self.bush_club, data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_accepts_valid_date_time(self):
        form = ScheduleMeetingForm(club=self.bush_club,data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_past_date(self):
        self.form_input['date'] = self.yesterday
        form = ScheduleMeetingForm(club=self.bush_club,data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_current_date_past_time(self):
        self.form_input['date'] = self.today
        self.form_input['time'] = self.past_time
        form = ScheduleMeetingForm(club=self.bush_club,data=self.form_input)
        self.assertFalse(form.is_valid())
