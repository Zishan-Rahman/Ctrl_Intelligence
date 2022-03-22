"""Tests of the create chats view."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Application, Message, Chat
from bookclub.tests.helpers import reverse_with_next
from django.contrib import messages
from django.core.exceptions import ValidationError


class InviteTestCases(TestCase):
    """Tests of the create chats view."""

    fixtures = ['bookclub/tests/fixtures/default_users.json' , 'bookclub/tests/fixtures/default_clubs.json', 'bookclub/tests/fixtures/default_applications.json']

    def setUp(self):
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.bush_club = Club.objects.get(pk=1)
        self.bush_club.make_member(self.john)
        self.url = reverse('invite_message', kwargs={'club_id': self.bush_club.id, 'user_id': self.john.id})

    def test_invite_url(self):
        self.assertEqual(self.url, f'/invite/{self.john.id}/1/')

    def test_invite_uses_correct_template(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('user_profile', kwargs={'user_id': self.john.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile.html')

    def test_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_user_profile_has_invite(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('user_profile', kwargs={'user_id': self.john.id}))
        html = response.content.decode('utf8')
        self.assertIn('id="Invite"', html)