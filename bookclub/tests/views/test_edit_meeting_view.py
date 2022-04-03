"""Unit tests for the Edit Meeting view"""
from datetime import datetime, timedelta
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import ScheduleMeetingForm
from bookclub.models import Club, Meeting, User
from bookclub.tests.helpers import reverse_with_next

class EditMeetingViewTestCase(TestCase):
    """Test case for the Edit Meeting View.

    The view utilises the ScheduleMeetingForm used for creating meetings.

    Inspired by Fathima Jamal-Deen's edit profile view tests."""

    fixtures = [
        "bookclub/tests/fixtures/default_users.json",
        "bookclub/tests/fixtures/default_clubs.json"
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.sam = User.objects.get(pk=4)
        self.club = Club.objects.get(name="Bush House Book Club")
        self.meeting = Meeting.objects.create(
            date="2023-03-03",
            start_time="22:30:00",
            club=self.club,
            address="youtube.com"
        )
        self.url = reverse('edit_meeting', kwargs={'club_id':self.club.id, 'meeting_id':self.meeting.id})
        self.form_input = {
            'date': '2024-02-21',
            'start_time': '23:30:00',
            'address': 'example.com'
        }

    def test_edit_meeting_url(self):
        """Testing the edit meeting url."""
        self.assertEqual(self.url, f'/club_profile/{self.club.id}/meetings/{self.meeting.id}/edit')

    def test_edit_meeting_uses_correct_template(self):
        """Testing if edit meeting uses correct template."""
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(str(response.context['user']), 'johndoe@bookclub.com')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_meeting.html')

    def test_cannot_hijack_edit_meeting(self):
        """Test for a hijacked edit meeting page."""
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('edit_meeting', kwargs={'club_id': self.club.id, 'meeting_id': self.meeting.id}), follow=True)
        redirect_url = reverse('club_list')
        messages_list = list(response.context['messages'])
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_cannot_hijack_edit_meeting_non_owner_organiser(self):
        """Test for a hijacked edit meeting view ."""
        self.club.make_member(self.sam)
        self.club.make_organiser(self.sam)
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('edit_meeting', kwargs={'club_id': self.club.id, 'meeting_id': self.meeting.id}), follow=True)
        redirect_url = reverse('club_list')
        messages_list = list(response.context['messages'])
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_get_meeting(self):
        """Testing for meeting page."""
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ScheduleMeetingForm))
        self.assertEqual(form.instance, self.meeting)

    def test_get_edit_meeting_view_redirects_when_not_logged_in(self):
        """Test if not logged in, redirect to edit meeting."""
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_meeting_update_with_past_date(self):
        """Testing for an unsuccessful meeting update due to past date."""
        self.form_input['date'] = "2000-01-01"
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        response = self.client.post(self.url, self.form_input, club=self.club, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ScheduleMeetingForm))
        self.assertTrue(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertFalse(Meeting.objects.filter(date=self.form_input['date'], club = self.club).exists())

        self.assertFalse(Meeting.objects.filter(date=self.form_input['date'], club = self.club).exists())

    def test_unsuccessful_meeting_update_with_past_time(self):
        """Testing for an unsuccessful meeting update due to past time."""
        self.form_input['date'] = datetime.now().date()
        self.form_input['start_time'] = (datetime.now() + timedelta(minutes=-2)).time().isoformat(timespec='seconds') #From python documentation https://docs.python.org/3/library/datetime.html#time-objects
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        response = self.client.post(self.url, self.form_input, club=self.club, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ScheduleMeetingForm))
        self.assertTrue(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertFalse(Meeting.objects.filter(date=self.form_input['date'], club = self.club).exists())

    def test_successful_meeting_update(self):
        """Testing for a successful meeting update."""
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        response = self.client.post(self.url, self.form_input, club=self.club, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.assertTrue(Meeting.objects.filter(date=self.form_input['date'], club = self.club).exists())


    def test_post_meeting_redirects_when_not_logged_in(self):
        """Test if not logged in, redirect post meeting."""
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
