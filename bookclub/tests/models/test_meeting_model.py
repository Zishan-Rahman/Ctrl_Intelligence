"""Unit tests for the Meeting model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import *
from datetime import timedelta, date, time, datetime


class MeetingModelTestCase(TestCase):
    """Test case for the Meeting model of Bookwise"""

    fixtures = [
        # Some already defined clubs and users to use for our application
        "bookclub/tests/fixtures/default_clubs.json",
        "bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.john = User.objects.get(pk=1)
        self.jane = User.objects.get(pk=2)
        self.bush_club = Club.objects.get(pk=1)
        self.somerset_club = Club.objects.get(pk=2)
        self.address = "example.com"
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)
        last_hour_date_time = datetime.now() - timedelta(hours=1)
        next_hour_date_time = datetime.now() + timedelta(hours=1)
        self.past_time = time(last_hour_date_time.hour, 0)
        self.future_time = time(next_hour_date_time.hour, 0)
        self.meeting = Meeting.objects.create(start_time=self.future_time, date=self.tomorrow, address=self.address, club=self.bush_club)

    def test_meeting_data_is_valid(self):
        """Test if the newly set-up meeting is valid at the moment."""
        self._assert_meeting_is_valid()

    def test_time_cannot_be_null(self):
        """Test if a meeting with no time is invalid."""
        self.meeting.start_time = None
        self._assert_meeting_is_invalid()

    def test_date_cannot_be_null(self):
        """Test if a meeting with no date is invalid."""
        self.meeting.date = None
        self._assert_meeting_is_invalid()

    def test_club_cannot_be_null(self):
        """Test if a meeting with no club is invalid."""
        self.meeting.club = None
        self._assert_meeting_is_invalid()

    def test_address_cannot_be_null(self):
        """Test if a meeting with no address is invalid."""
        self.meeting.address = None
        self._assert_meeting_is_invalid()

    # Test getters

    def test_meeting_club_getter_works(self):
        """Testing the meeting club getter method in the Meeting model."""
        self.assertEqual(self.meeting.get_meeting_club(), self.meeting.club)

    def test_meeting_date_getter_works(self):
        """Testing the meeting date getter method in the Meeting model."""
        self.assertEqual(self.meeting.get_meeting_date(), self.meeting.date)

    def test_meeting_start_time_getter_works(self):
        """Testing the meeting time getter method in the Meeting model."""
        self.assertEqual(self.meeting.get_meeting_start_time(), self.meeting.start_time)

    def test_meeting_address_getter_works(self):
        """Testing the meeting address getter method in the Meeting model."""
        self.assertEqual(self.meeting.get_meeting_address(), self.meeting.address)

    def _assert_meeting_is_valid(self):
        """Test if the meeting is valid."""
        try:
            self.meeting.full_clean()
        except ValidationError:
            self.fail('Test meeting should be valid')

    def _assert_meeting_is_invalid(self):
        """Test if the meeting is invalid"""
        with self.assertRaises(ValidationError):
            self.meeting.full_clean()
