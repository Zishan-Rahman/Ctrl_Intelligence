"""Unit tests for the Create Chats View"""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Application, Chat
from bookclub.tests.helpers import reverse_with_next
from django.contrib import messages


class CreateChatsViewTestCase(TestCase):
    """Test case for the Create Chats view"""

    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.url = reverse('create_chat')
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')


    def test_create_chats_url(self):
        """Testing the create chats url."""
        self.assertEqual(self.url, '/inbox/create_chat')

    def test_create_chat_uses_correct_template(self):
        """Testing if create chat uses correct template."""
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(reverse('create_chat'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_chat.html')

    def test_create_chat_has_correct_details(self):
        """Testing if create chat uses correct details."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('create_chat'))
        html = response.content.decode('utf8')
        self.assertIn('<a', html)
        self.assertIn('Start a Conversation!', html)

    def test_successful_creation(self):
        self.client.login(email=self.john.email, password='Password123')
        beforeCount = Chat.objects.count()
        response = self.client.post(reverse('create_chat'), {"email":"janedoe@bookclub.com"}, follow=True)
        response_url = reverse('chat', kwargs={'pk':1})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'chat.html')
        afterCount = Chat.objects.count()
        self.assertEqual(beforeCount+1, afterCount)

    def test_creation_with_yourself(self):
        self.client.login(email=self.john.email, password='Password123')
        beforeCount = Chat.objects.count()
        response = self.client.post(reverse('create_chat'), {"email":"johndoe@bookclub.com"}, follow=True)
        response_url = reverse('create_chat')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'create_chat.html')
        afterCount = Chat.objects.count()
        self.assertEqual(beforeCount, afterCount)

    def test_creation_with_already_existing_and_same_sender(self):
        chat = Chat.objects.create(user=self.john, receiver=self.jane)
        self.client.login(email=self.john.email, password='Password123')
        beforeCount = Chat.objects.count()
        response = self.client.post(reverse('create_chat'), {"email":"janedoe@bookclub.com"}, follow=True)
        response_url = reverse('chat', kwargs={'pk':chat.pk})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'chat.html')
        afterCount = Chat.objects.count()
        self.assertEqual(beforeCount, afterCount)

    def test_creation_with_already_existing_and_different_sender(self):
        chat = Chat.objects.create(user=self.jane, receiver=self.john)
        self.client.login(email=self.john.email, password='Password123')
        beforeCount = Chat.objects.count()
        response = self.client.post(reverse('create_chat'), {"email":"janedoe@bookclub.com"}, follow=True)
        response_url = reverse('chat', kwargs={'pk':chat.pk})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'chat.html')
        afterCount = Chat.objects.count()
        self.assertEqual(beforeCount, afterCount)

    def test_creation_with_nonexistent_user(self):
        self.client.login(email=self.john.email, password='Password123')
        beforeCount = Chat.objects.count()
        response = self.client.post(reverse('create_chat'), {"email":"fakeuser@bookclub.com"}, follow=True)
        response_url = reverse('create_chat')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'create_chat.html')
        afterCount = Chat.objects.count()
        self.assertEqual(beforeCount, afterCount)

    def test_creation_with_not_email(self):
        self.client.login(email=self.john.email, password='Password123')
        beforeCount = Chat.objects.count()
        response = self.client.post(reverse('create_chat'), {"email":"asdadadadads"}, follow=True)
        response_url = reverse('create_chat')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'create_chat.html')
        afterCount = Chat.objects.count()
        self.assertEqual(beforeCount, afterCount)


    def test_successful_creation_from_profile(self):
        self.client.login(email=self.john.email, password='Password123')
        beforeCount = Chat.objects.count()
        response = self.client.post(reverse('create_chat_from_profile', kwargs={"user_id":2}), follow=True)
        response_url = reverse('chat', kwargs={'pk':1})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'chat.html')
        afterCount = Chat.objects.count()
        self.assertEqual(beforeCount+1, afterCount)

    def test_creation_with_already_existing_and_same_sender_from_profile(self):
        chat = Chat.objects.create(user=self.john, receiver=self.jane)
        self.client.login(email=self.john.email, password='Password123')
        beforeCount = Chat.objects.count()
        response = self.client.post(reverse('create_chat_from_profile', kwargs={"user_id":2}), follow=True)
        response_url = reverse('chat', kwargs={'pk':chat.pk})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'chat.html')
        afterCount = Chat.objects.count()
        self.assertEqual(beforeCount, afterCount)

    def test_creation_with_already_existing_and_different_sender_from_profile(self):
        chat = Chat.objects.create(user=self.jane, receiver=self.john)
        self.client.login(email=self.john.email, password='Password123')
        beforeCount = Chat.objects.count()
        response = self.client.post(reverse('create_chat_from_profile', kwargs={"user_id":2}), follow=True)
        response_url = reverse('chat', kwargs={'pk':chat.pk})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'chat.html')
        afterCount = Chat.objects.count()
        self.assertEqual(beforeCount, afterCount)

    def test_creation_with_nonexistent_user(self):
        self.client.login(email=self.john.email, password='Password123')
        beforeCount = Chat.objects.count()
        response = self.client.post(reverse('create_chat_from_profile', kwargs={"user_id":100}), follow=True)
        response_url = reverse('create_chat')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'create_chat.html')
        afterCount = Chat.objects.count()
        self.assertEqual(beforeCount, afterCount)
