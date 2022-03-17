"""Tests of the feed view."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import PostForm
from bookclub.models import User , Club
from bookclub.tests.helpers import create_posts, reverse_with_next


class PostViewTestCase(TestCase):
    """Tests of the feed view."""

    fixtures = ["bookclub/tests/fixtures/default_users.json",
                "bookclub/tests/fixtures/default_clubs.json"]


    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.club = Club.objects.get(name='Bush House Book Club')
        self.club.make_member(self.user)
        self.url = reverse('posts', kwargs={'club_id': self.club.id})

    def test_post_url(self):
        self.assertEqual(self.url, f'/club_profile/{self.club.id}/new_post')

    def test_get_posts(self):
        self.client.login(email=self.user.email, password=self.user.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(response, 'feed.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PostForm))
        self.assertFalse(form.is_bound)