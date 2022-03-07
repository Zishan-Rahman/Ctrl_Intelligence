"""Tests for the edit club view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import EditClubForm
from bookclub.models import *
from bookclub.tests.helpers import reverse_with_next

class ProfileViewTest(TestCase):
    """Test suite for the profile view."""

    fixtures = [
        'bookclub/tests/fixtures/default_users.json',
        'bookclub/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.club = Club.objects.get(pk=1)
        self.url = '/club_profile/1/edit/'
        self.form_input = {
            'name': 'Bush House Book Club Remastered',
            'description': 'New description',
            'location': 'Strand, London, England',
            'meeting_online':False
        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/club_profile/1/edit/')

    def test_get_club_profile(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditClubForm))

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccesful_club_update(self):
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        self.form_input['name'] = ''
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditClubForm))
        self.assertTrue(form.is_bound)
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, 'Bush House Book Club')
        self.assertEqual(self.club.description, 'Bush House Official Book Club!')
        self.assertEqual(self.club.location, 'Strand, London')
        self.assertEqual(self.club.meeting_online, True)

    def test_unsuccessful_club_update_due_to_duplicate_name(self):
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        self.form_input['name'] = 'Somerset House Book Club'
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditClubForm))
        self.assertTrue(form.is_bound)
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, 'Bush House Book Club')
        self.assertEqual(self.club.description, 'Bush House Official Book Club!')
        self.assertEqual(self.club.location, 'Strand, London')
        self.assertEqual(self.club.meeting_online, True)

    def test_succesful_profile_update(self):
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_selector')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club_switcher.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, 'Bush House Book Club Remastered')
        self.assertEqual(self.club.description, 'New description')
        self.assertEqual(self.club.location, 'Strand, London, England')
        self.assertEqual(self.club.meeting_online, False)
