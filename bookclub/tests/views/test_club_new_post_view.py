# Adapted from Clucker project
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.shortcuts import redirect
from bookclub.forms import PostForm
from bookclub.models import User, Club, Post
from bookclub.tests.helpers import reverse_with_next, LogInTester

class NewPostTest(TestCase):

    fixtures = ["bookclub/tests/fixtures/default_users.json",
                "bookclub/tests/fixtures/default_clubs.json"]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.bush_club.make_member(self.user)
        self.url = reverse('new_post' ,  kwargs={'club_id': self.bush_club.id} )
        self.data = { 'text': 'This is a club post' }

    def test_new_post_url(self):
        self.assertEqual(self.url,f'/club_profile/{self.bush_club.id}/new_post/')

    def test_get_new_post_is_forbidden(self):
        self.client.login(email=self.user.email, password="Password123")
        user_count_before = Post.objects.count()
        response = self.client.get(self.url, follow=True)
        user_count_after = Post.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertEqual(response.status_code, 405)

    def test_post_new_post_redirects_when_not_logged_in(self):
        user_count_before = Post.objects.count()
        redirect_url = reverse('login')
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        user_count_after = Post.objects.count()
        self.assertEqual(user_count_after, user_count_before)

    def test_successful_new_post(self):
        self.client.login(email=self.user.email, password="Password123")
        user_count_before = Post.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Post.objects.count()
        self.assertEqual(user_count_after, user_count_before+1)
        new_post = Post.objects.latest('created_at')
        self.assertEqual(self.user, new_post.author)
        response_url = reverse('club_profile', kwargs={'club_id': self.bush_club.id} )
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'club_profile.html')

    def test_unsuccessful_new_post(self):
        self.client.login(email=self.user.email, password="Password123")
        user_count_before = Post.objects.count()
        self.data['text'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Post.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertTemplateUsed(response, 'feed.html')

    def test_cannot_create_post_for_other_user(self):
        self.client.login(email=self.user.email, password="Password123")
        other_user = User.objects.get(email='janedoe@bookclub.com')
        self.data['author'] = other_user.id
        user_count_before = Post.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Post.objects.count()
        self.assertEqual(user_count_after, user_count_before+1)
        new_post = Post.objects.latest('created_at')
        self.assertEqual(self.user, new_post.author)