"""Tests of the create chats view."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Application, Chat, Message
from bookclub.tests.helpers import reverse_with_next
from django.contrib import messages


class ChatViewTestCase(TestCase):
    """Tests of the chat view."""

    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.url = reverse('create_chat')
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')
        self.chat = Chat.objects.create(user=self.john, receiver=self.jane)

    def test_chat_access_if_not_yours(self):
        """Tests to check if you can access chats that you dont belong to"""
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(reverse('chat', kwargs={'pk':self.chat.pk}))
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)


