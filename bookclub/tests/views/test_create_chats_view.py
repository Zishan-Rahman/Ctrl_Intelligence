"""Tests of the create chats view."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Application
from bookclub.tests.helpers import reverse_with_next
from django.contrib import messages


class CreateChatsViewTestCase(TestCase):
    """Tests of the create chats view."""

    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.url = reverse('create_chat')
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')


    def test_create_chats_url(self):
        self.assertEqual(self.url, '/inbox/create_chat')

    def test_create_chat_uses_correct_template(self):
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(reverse('create_chat'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_chat.html')

    def test_create_chat_has_correct_details(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('create_chat'))
        html = response.content.decode('utf8')
        self.assertIn('<a', html)
        self.assertIn('Start a Conversation!', html)
