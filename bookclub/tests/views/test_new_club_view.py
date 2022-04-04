"""Unit tests of the create club view"""
"""Adapted from the Chess club project"""
from django.test import TestCase
from bookclub.forms import ClubForm
from django.urls import reverse
from bookclub.models import User, Club
from django.contrib import messages

class NewClubViewTestCase(TestCase):
    """Unit tests of the create club view"""

    fixtures = [
        "bookclub/tests/fixtures/default_users.json"
    ]

    def setUp(self):
        self.url = reverse('new_club')
        self.owner = User.objects.get(email='johndoe@bookclub.com')
        self.form_input = {
            'name': 'BookBusters',
            'description': 'Crime and Mystery',
            'location': 'Cardiff',
            'meeting_type': False,
            'organiser_has_owner_privilege': True
        }
    
    def test_create_club_url(self):
        self.assertEqual(self.url, '/new_club/')

    def test_get_create_club(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_create_club(self):
        self.client.login(email=self.owner.email, password='Password123')
        before_count = Club.objects.count()
        self.form_input['name'] = ""
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubForm))
        self.assertTrue(form.is_bound)

    def test_successful_create_club(self):
        self.client.login(email=self.owner.email, password='Password123')
        before_count = Club.objects.count()
        form = ClubForm(data=self.form_input)
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse("club_selector")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.assertEqual(messages_list[0].message,
                         "Club has been created!")
        club = Club.objects.get(name='BookBusters')
        self.assertEqual(club.name, 'BookBusters')
        self.assertEqual(club.location, 'Cardiff')
        self.assertEqual(club.description, 'Crime and Mystery')

    def test_club_page_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = "/login/?next=/new_club/"
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)