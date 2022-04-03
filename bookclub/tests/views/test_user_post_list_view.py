from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, UserPost
from bookclub.tests.helpers import reverse_with_next
from django.contrib import messages


class UserPostViewTestCase(TestCase):
    """Tests of the user post list view."""

    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.url = reverse('user_posts')
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')
        self.sam = User.objects.get(email='samdoe@bookclub.com')

        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.somerset_club = Club.objects.get(name='Somerset House Book Club')
        self.strand_club = Club.objects.get(name='Strand House Book Club')

        self.john._follow(self.jane)
        UserPost.objects.create(author=self.jane, text="This is a user post.")

    def test_user_post_url(self):
        """Tests to check the user post list url"""
        self.assertEqual(self.url, '/user_posts/')

    def test_user_post_uses_correct_template(self):
        """Tests to check the user post list uses the correct template"""
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(reverse('user_posts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_posts.html')

    def test_user_posts_has_correct_details(self):
        """Tests to check the user post list has the correct details"""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('user_posts'))
        html = response.content.decode('utf8')
        self.assertIn('Jane Doe', html)
        self.assertIn('This is a user post.', html)

    def test_no_user_posts(self):
        """Tests to check the user post list has the correct details if no posts are present"""
        self.client.login(email=self.joe.email, password='Password123')
        user_posts = UserPost.objects.all()
        for p in user_posts:
            p.delete()
        response = self.client.get(reverse('user_posts'))
        html = response.content.decode('utf8')
        self.assertIn('There are no posts', html)
        self.assertNotIn('<td>', html)
        self.assertNotIn('</td>', html)

    def test_get_user_posts_list_redirects_when_not_logged_in(self):
        """Tests to check the user post list redirects non-logged in users when trying to access it"""
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_user_post_list_with_pagination(self):
        """Tests to check the user post list paginates correctly"""
        self.client.login(email=self.john.email, password='Password123')
        self._create_test_user_posts(settings.POSTS_PER_PAGE * 2 + 3 - 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_posts.html')
        self.assertEqual(len(response.context['page_obj']), settings.POSTS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('user_posts') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_posts.html')
        self.assertEqual(len(response.context['page_obj']), settings.POSTS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('user_posts') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_posts.html')
        self.assertEqual(len(response.context['page_obj']), settings.POSTS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('user_posts') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_posts.html')
        self.assertEqual(len(response.context['page_obj']), 3)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())

    def _create_test_user_posts(self, my_posts_count=10):
        """Creates user posts"""
        posts = []
        
        for id in range(1, my_posts_count + 1, 1):
            posts.append(UserPost.objects.create(author=self.jane, text="This is a user post."))
