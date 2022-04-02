# Adapted from Clucker project

"""Tests of the feed view."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.shortcuts import redirect
from bookclub.forms import PostForm
from bookclub.models import User, Club, Post
from bookclub.tests.helpers import create_posts, reverse_with_next, LogInTester


class ClubFeedViewTestCase(TestCase, LogInTester):
    """Tests of the feed view."""

    fixtures = ["bookclub/tests/fixtures/default_users.json",
                "bookclub/tests/fixtures/default_clubs.json"]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.bush_club.make_member(self.user)
        self.url = reverse('feed', kwargs={'club_id': self.bush_club.id})

    def test_post_club_feed(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_club_posts(2)
        form_data = {'text': 'This is bush house book club post'}
        form = PostForm(form_data)
        response = self.client.post(self.url, {"author": self.user, "club": self.bush_club, "form": form})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self._is_logged_in())
        self.assertTrue(form.is_valid)
        response = self.client.get(self.url)

    def test_club_feed_url(self):
        self.assertEqual(self.url, f'/club_profile/{self.bush_club.id}/feed/')

    def test_get_club_feed(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self._create_test_club_posts(settings.POSTS_PER_PAGE*2+3)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')
        self.assertTrue(self._is_logged_in())

    def test_get_club_feed_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertFalse(self._is_logged_in())

    def test_get_club_feed_with_pagination(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_club_posts(settings.POSTS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')
        self.assertEqual(
            len(response.context['page_obj']), settings.POSTS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('feed', kwargs={'club_id': self.bush_club.id}) + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')
        self.assertEqual(
            len(response.context['page_obj']), settings.POSTS_PER_PAGE)
        page_two_url = reverse('feed', kwargs={'club_id': self.bush_club.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')
        self.assertEqual(
            len(response.context['page_obj']), settings.POSTS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('feed', kwargs={'club_id': self.bush_club.id}) + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')
        self.assertEqual(
            len(response.context['page_obj']), 2)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())
        
    def test_club_feed_view_context_data(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_club_posts(settings.POSTS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(context['user'], self.user)
        self.assertTrue(context['form'])
        self.assertEqual(context['club'], self.bush_club)
        self.assertEqual(len(context['posts']), len(Post.objects.filter(club=self.bush_club)))
        self.assertEqual(len(response.context['page_obj']), settings.POSTS_PER_PAGE)
        

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

    def _create_test_club_posts(self, club_posts_count=10):
        for id in range(1, club_posts_count+1, 1):
            user = User.objects.create(
                email=f'user{id}@test.org',
                password='Password123',
                first_name=f'First{id}',
                last_name=f'Last{id}',
                public_bio=f'Bio {id}',
                favourite_genre=f'genre {id}',
                location=f'City {id}',
                age=18+id
            )
            Post.objects.create(
                author=user,
                club=self.bush_club,
                text=f'Test club posts {id}'
            )

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()
