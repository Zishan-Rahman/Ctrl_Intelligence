"""Unit tests for the Follow View"""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import reverse_with_next


class FollowViewFollowTest(TestCase):
    """Test case for the Follow View"""
    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.followee= User.objects.get(email='janedoe@bookclub.com')
        self.url = reverse('follow_from_user_profile', kwargs={'user_id': self.followee.id})

    def test_follow_toggle_url(self):
        """Testing the follow toggle url."""
        self.assertEqual(self.url,f'/user_profile/{self.followee.id}/follow/')

    def test_get_follow_toggle_redirects_when_not_logged_in(self):
        """Test when not logged in, redirect to follow toggle."""
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_follow_toggle_for_followee(self):
        """Testing for follow toggle for followees."""
        self.client.login(username=self.user.email, password='Password123')
        self.user.toggle_follow(self.followee)
        user_followers_before = self.user.follower_count()
        followee_followers_before = self.followee.follower_count()
        response = self.client.get(self.url, follow=True)
        user_followers_after = self.user.follower_count()
        followee_followers_after = self.followee.follower_count()
        self.assertEqual(user_followers_before, user_followers_after)
        self.assertEqual(followee_followers_before, followee_followers_after+1)
        response_url = reverse('user_profile', kwargs={'user_id': self.followee.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_profile.html')

    def test_get_follow_toggle_for_non_followee(self):
        """Testing for follow toggle for non-followees."""
        self.client.login(username=self.user.email, password='Password123')
        user_followers_before = self.user.follower_count()
        followee_followers_before = self.followee.follower_count()
        response = self.client.get(self.url, follow=True)
        user_followers_after = self.user.follower_count()
        followee_followers_after = self.followee.follower_count()
        self.assertEqual(user_followers_before, user_followers_after)
        self.assertEqual(followee_followers_before+1, followee_followers_after)
        response_url = reverse('user_profile', kwargs={'user_id': self.followee.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_profile.html')
