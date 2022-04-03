"""Unit tests for the Club Post View"""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Post
from bookclub.tests.helpers import reverse_with_next
from django.contrib import messages


class ClubPostViewTestCase(TestCase):
    """Test case for the Club Post view"""

    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.url = reverse('club_posts')
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')
        self.sam = User.objects.get(email='samdoe@bookclub.com')

        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.somerset_club = Club.objects.get(name='Somerset House Book Club')
        self.strand_club = Club.objects.get(name='Strand House Book Club')

        Post.objects.create(author=self.joe, club=self.bush_club, text="This is a club post.")

    def test_club_post_url(self):
        """Testing the user post url."""
        self.assertEqual(self.url, '/club_posts/')

    def test_club_post_uses_correct_template(self):
        """Testing if the club post uses correct template."""
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(reverse('club_posts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_posts.html')

    def test_club_posts_has_correct_details(self):
        """Testing if the club post has the correct details."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('club_posts'))
        html = response.content.decode('utf8')
        self.assertIn('Bush House Book Club', html)
        self.assertIn('John Doe', html)
        self.assertIn('This is a club post.', html)

    def test_no_club_posts(self):
        """Testing if no club posts are made."""
        self.client.login(email=self.joe.email, password='Password123')
        club_posts = Post.objects.all()
        for p in club_posts:
            p.delete()
        response = self.client.get(reverse('club_posts'))
        html = response.content.decode('utf8')
        self.assertIn('There are no posts', html)
        self.assertNotIn('<td>', html)
        self.assertNotIn('</td>', html)

    def test_get_club_posts_list_redirects_when_not_logged_in(self):
        """Test if not logged in, redirect to club posts"""
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_club_post_list_with_pagination(self):
        """Testing for club post list with pagination."""
        self.client.login(email=self.john.email, password='Password123')
        self._create_test_club_posts(settings.POSTS_PER_PAGE * 2 + 3 - 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_posts.html')
        self.assertEqual(len(response.context['page_obj']), settings.POSTS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('club_posts') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_posts.html')
        self.assertEqual(len(response.context['page_obj']), settings.POSTS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('club_posts') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_posts.html')
        self.assertEqual(len(response.context['page_obj']), settings.POSTS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('club_posts') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_posts.html')
        self.assertEqual(len(response.context['page_obj']), 3)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())

    def _create_test_club_posts(self, my_posts_count=10):
        """Creation of a club post."""
        posts = []

        for id in range(1, my_posts_count + 1, 1):
            posts.append(Post.objects.create(author=self.john, club=self.bush_club, text="This is a club post."))
