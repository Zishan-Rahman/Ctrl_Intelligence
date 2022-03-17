#adapted from clucker
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import PostForm
from bookclub.models import User , Club
from bookclub.tests.helpers import create_posts, reverse_with_next


class FeedViewTestCase(TestCase):
    """Tests of the feed view."""

    fixtures = ["bookclub/tests/fixtures/default_users.json","bookclub/tests/fixtures/default_clubs.json"]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.club = Club.objects.get(name='Bush House Book Club')
        self.url = reverse('feed', kwargs={'club_id': self.club.id})

    def test_feed_url(self):
        self.assertEqual(self.url, f'/club_profile/{self.club.id}/feed/')

    def test_get_feed(self):
        self.client.login(email=self.user.email, password= self.user.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PostForm))
        self.assertFalse(form.is_bound)