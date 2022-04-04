# Adapted from Clucker project
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.shortcuts import redirect
from bookclub.forms import UserPostForm
from bookclub.models import User, Club, UserPost
from bookclub.tests.helpers import reverse_with_next, LogInTester

class NewUserPostTest(TestCase):

    fixtures = ["bookclub/tests/fixtures/default_users.json",
                "bookclub/tests/fixtures/default_clubs.json"]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.bush_club.make_member(self.user)
        self.url = reverse('user_new_post' ,  kwargs={'user_id': self.user.id} )
        self.data = { 'text': 'This is a user post' }

    def test_new_user_post_url(self):
        self.assertEqual(self.url,f'/user_profile/{self.user.id}/new_post/')

    def test_get_new_user_post_is_forbidden(self):
        self.client.login(email=self.user.email, password="Password123")
        user_count_before = UserPost.objects.count()
        response = self.client.get(self.url, follow=True)
        user_count_after = UserPost.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertEqual(response.status_code, 405)

    def test_user_post_new_user_post_redirects_when_not_logged_in(self):
        user_count_before = UserPost.objects.count()
        redirect_url = reverse('login')
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        user_count_after = UserPost.objects.count()
        self.assertEqual(user_count_after, user_count_before)

    def test_successful_new_user_post(self):
        self.client.login(email=self.user.email, password="Password123")
        user_count_before = UserPost.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = UserPost.objects.count()
        self.assertEqual(user_count_after, user_count_before+1)
        new_UserPost = UserPost.objects.latest('created_at')
        self.assertEqual(self.user, new_UserPost.author)
        response_url = reverse('profile')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'user_profile.html')

    def test_unsuccessful_new_user_post(self):
        self.client.login(email=self.user.email, password="Password123")
        user_count_before = UserPost.objects.count()
        self.data['text'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = UserPost.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertTemplateUsed(response, 'user_feed.html')

    def test_cannot_create_user_post_for_other_user(self):
        self.client.login(email=self.user.email, password="Password123")
        other_user = User.objects.get(email='janedoe@bookclub.com')
        self.data['author'] = other_user.id
        user_count_before = UserPost.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = UserPost.objects.count()
        self.assertEqual(user_count_after, user_count_before+1)
        new_UserPost = UserPost.objects.latest('created_at')
        self.assertEqual(self.user, new_UserPost.author)