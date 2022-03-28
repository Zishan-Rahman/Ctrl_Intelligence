# Adapted from Clucker project

"""Tests of the feed view."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import UserPostForm
from bookclub.models import User
from bookclub.tests.helpers import create_posts, reverse_with_next, LogInTester


class UserFeedViewTestCase(TestCase, LogInTester):
    """Tests of the user feed view."""

    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.url = reverse('user_feed', kwargs={'user_id': self.user.id})

    def test_feed_url(self):
        self.assertEqual(self.url, f'/user_profile/{self.user.id}/user_feed/')

    def test_get_feed(self):
        self.client.login(email='johndoe@bookclub.com', password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_feed.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserPostForm))
        self.assertFalse(form.is_bound)

    def test_get_feed_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._is_logged_in())

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()
