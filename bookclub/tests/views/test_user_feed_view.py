# Adapted from Clucker project

"""Tests of the feed view."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import UserPostForm
from bookclub.models import User, UserPost
from bookclub.tests.helpers import create_posts, reverse_with_next, LogInTester


class UserFeedViewTestCase(TestCase, LogInTester):
    """Tests of the feed view."""

    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.url = reverse('user_feed', kwargs={'user_id': self.user.id})

    def test_user_feed_url(self):
        self.assertEqual(self.url, f'/user_profile/{self.user.id}/user_feed/')

    def test_get_user_feed(self):
        self.client.login(email=self.user, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_feed.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserPostForm))
        self.assertFalse(form.is_bound)

    def test_get_user_feed_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._is_logged_in())

    def test_get_user_feed_with_pagination(self):
        self.client.login(email=self.user, password="Password123")
        self._create_test_user_posts(settings.POSTS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_feed.html')
        self.assertEqual(len(response.context['page_obj']), settings.POSTS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = self.url + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_feed.html')
        self.assertEqual(len(response.context['page_obj']), settings.POSTS_PER_PAGE)
        page_two_url = self.url + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_feed.html')
        self.assertEqual(len(response.context['page_obj']), settings.POSTS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = self.url + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_feed.html')
        self.assertEqual(len(response.context['page_obj']), 2)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())

    def _create_test_user_posts(self, user_posts_count=10):
        for id in range(1, user_posts_count+1, 1):
            UserPost.objects.create(
                author=self.user,
                text=f'Sample user posts {id}'
            )

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()
