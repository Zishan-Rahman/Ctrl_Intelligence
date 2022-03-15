"""Tests for the edit meeting view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import ScheduleMeetingForm
from bookclub.models import Club, Meeting, User
from bookclub.tests.helpers import reverse_with_next

class EditMeetingViewTestCase(TestCase):
    """Test suite for the edit meeting view.
    
    The view utilises the ScheduleMeetingForm used for creating meetings.
    
    Inspired by Fathima Jamal-Deen's edit profile view tests."""
    
    fixtures = [
        "bookclub/tests/fixtures/default_users.json",
        "bookclub/tests/fixtures/default_clubs.json"
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
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
        self.assertEqual(self.url, f'/club_profile/{self.club.id}/meetings/{self.meeting.id}/edit')

    def test_edit_meeting_uses_correct_template(self):
        login = self.client.login(email='johndoe@bookclub.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(str(response.context['user']), 'johndoe@bookclub.com')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_meeting.html')

    def test_get_meeting(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ScheduleMeetingForm))
        self.assertEqual(form.instance, self.meeting)

    def test_get_edit_meeting_view_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccesful_meeting_update(self):
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        self.form_input['email'] = 'BAD_email'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ScheduleMeetingForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'johndoe@bookclub.com')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.public_bio, "Im just an abstract concept!")
        self.assertEqual(self.user.favourite_genre, "Science fiction")
        self.assertEqual(self.user.location, "London")
        self.assertEqual(self.user.age, 39)

    def test_unsuccessful_meeting_update_due_to_duplicate_email(self):
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        self.form_input['email'] = 'janedoe@bookclub.com'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ScheduleMeetingForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'johndoe@bookclub.com')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.public_bio, "Im just an abstract concept!")
        self.assertEqual(self.user.favourite_genre, "Science fiction")
        self.assertEqual(self.user.location, "London")
        self.assertEqual(self.user.age, 39)

    def test_succesful_meeting_update(self):
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, club=self.club, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'johndoe2@bookclub.com')
        self.assertEqual(self.user.first_name, 'John2')
        self.assertEqual(self.user.last_name, 'Doe2')
        self.assertEqual(self.user.public_bio, 'New public_bio')
        self.assertEqual(self.user.favourite_genre, "Science fiction")
        self.assertEqual(self.user.location, "London")
        self.assertEqual(self.user.age, 39)

    def test_post_meeting_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
