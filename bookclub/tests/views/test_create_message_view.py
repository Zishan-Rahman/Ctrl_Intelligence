"""Unit tests for the Create Message View."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Application, Chat, Message
from bookclub.tests.helpers import reverse_with_next
from django.contrib import messages


class CreateMessageViewTestCase(TestCase):
    """Test case for the Create Message view."""

    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.url = reverse('create_chat')
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')
        self.chat = Chat.objects.create(user=self.john, receiver=self.jane)

    def test_successful_creation_when_user_isnt_receiver(self):
        """Testing for a succesfull message creation, from recipient."""
        self.client.login(email=self.john.email, password='Password123')
        beforeCount = Message.objects.count()
        response = self.client.post(reverse('create_message', kwargs={'pk':self.chat.pk}), {'message': "Message"}, follow=True)
        response_url = reverse('chat', kwargs={'pk':self.chat.pk})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'chat.html')
        afterCount = Message.objects.count()
        self.assertEqual(beforeCount+1, afterCount)

    def test_successful_creation_when_user_is_receiver(self):
        """Testing for a succesfull message creation when user is recipient."""
        self.client.login(email=self.jane.email, password='Password123')
        beforeCount = Message.objects.count()
        response = self.client.post(reverse('create_message', kwargs={'pk':self.chat.pk}), {'message': "Message two"}, follow=True)
        response_url = reverse('chat', kwargs={'pk':self.chat.pk})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'chat.html')
        afterCount = Message.objects.count()
        self.assertEqual(beforeCount+1, afterCount)
