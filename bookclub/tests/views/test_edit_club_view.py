"""Unit tests for the Edit Club View"""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import EditClubForm
from bookclub.models import *
from bookclub.tests.helpers import reverse_with_next


class EditClubViewTest(TestCase):
    """Test case for the Edit Club View"""

    fixtures = [
        'bookclub/tests/fixtures/default_users.json',
        'bookclub/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.sam = User.objects.get(pk=4)
        self.club = Club.objects.get(pk=1)
        self.url = '/club_profile/1/edit/'
        self.form_input = {
            'name': 'Bush House Book Club Remastered',
            'description': 'New description',
            'location': 'Strand, London, England',
            'meeting_online': False,
            'organiser_owner': True
        }

    def test_profile_url(self):
        """Testing the edit club profile url."""
        self.assertEqual(self.url, '/club_profile/1/edit/')

    def test_get_club_profile(self):
        """Testing for club profile page."""
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditClubForm))

    def test_get_profile_redirects_when_not_logged_in(self):
        """Test if not logged in, redirect to club profile."""
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_cannot_hijack_edit_club(self):
        """Testing for a hijacked edit club page."""
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('edit_club', kwargs={'c_pk': self.club.id}), follow=True)
        redirect_url = reverse('club_list')
        messages_list = list(response.context['messages'])
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_unsuccessful_club_update(self):
        """Testing for unsuccessful club profile updates."""
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
        """Testing for unsuccessful club profile updates due to duplicate name."""
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

    def test_successful_profile_update(self):
        """Testing for successful club profile update."""
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_profile', kwargs={'club_id': 1})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club_profile.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, 'Bush House Book Club Remastered')
        self.assertEqual(self.club.description, 'New description')
        self.assertEqual(self.club.location, 'Strand, London, England')
        self.assertEqual(self.club.meeting_online, False)
