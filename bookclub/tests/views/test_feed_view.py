# Adapted from Clucker project

"""Tests of the feed view."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import PostForm
from bookclub.models import User, Club
from bookclub.tests.helpers import create_posts, reverse_with_next, LogInTester


class FeedViewTestCase(TestCase, LogInTester):
    """Tests of the feed view."""

    fixtures = ["bookclub/tests/fixtures/default_users.json",
                "bookclub/tests/fixtures/default_clubs.json"]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.bush_club.make_member(self.user)
        self.url = reverse('feed', kwargs={'club_id': self.bush_club.id})

    def test_feed_url(self):
        self.assertEqual(self.url, f'/club_profile/{self.bush_club.id}/feed/')

    def test_get_feed(self):
        self.client.login(email='johndoe@bookclub.com', password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PostForm))
        self.assertFalse(form.is_bound)

    def test_get_feed_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._is_logged_in())

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()
