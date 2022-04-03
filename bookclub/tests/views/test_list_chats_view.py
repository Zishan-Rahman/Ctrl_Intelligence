"""Unit tests for the List Chats View"""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Application
from bookclub.tests.helpers import reverse_with_next
from django.contrib import messages


class ListChatsViewTestCase(TestCase):
    """Test case for the List Chats View"""

    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.url = reverse('inbox')
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')


    def test_inbox_url(self):
        """Testing the inbox url."""
        self.assertEqual(self.url, '/inbox/')

    def test_inbox_uses_correct_template(self):
        """Testing if inbox uses correct template."""
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(reverse('inbox'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inbox.html')

    def test_inbox_has_correct_details(self):
        """Testing if inbox has the correct details."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('inbox'))
        html = response.content.decode('utf8')
        self.assertIn('Your Chats', html)
