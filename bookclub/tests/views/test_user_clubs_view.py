"""Unit tests for the User Clubs View"""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from bookclub.models import User, Club
from bookclub.tests.helpers import LogInTester, reverse_with_next


# user clubs test case is adapted from the clubs list test case

class UserClubsListViewTestCase(TestCase, LogInTester):
    """Test case for the User Clubs view"""

    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.john = User.objects.get(pk=1)
        self.jane = User.objects.get(pk=2)
        self.url = reverse('user_clubs', kwargs={'user_id': self.jane.id})
        self.url2 = reverse('user_clubs', kwargs={'user_id': self.john.id})

    def test_clubs_list_url(self):
        """Testing the user club list url."""
        self.assertEqual(self.url, f'/user_profile/{self.jane.id}/clubs/')

    def test_correct_user_clubs_list_template(self):
        """Testing if user club list uses correct template."""
        self.client.login(email=self.john.email, password="Password123")
        response = self.client.get(self.url)
        self._is_logged_in()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_clubs.html")

    def test_get_clubs_list_redirects_when_not_logged_in(self):
        """Test if not logged in, redirect to clubs list."""
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_user_clubs_list_with_pagination(self):
        """Test for user clubs list with pagination."""
        self.client.login(email=self.john.email, password='Password123')
        self._create_test_clubs(settings.CLUBS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_clubs.html')
        self.assertEqual(len(response.context['all_clubs']), settings.CLUBS_PER_PAGE*2+3-1)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), settings.CLUBS_PER_PAGE)
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('user_clubs', kwargs={'user_id': self.jane.id}) + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_clubs.html')
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), settings.CLUBS_PER_PAGE)
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('user_clubs', kwargs={'user_id': self.jane.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_clubs.html')
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), settings.CLUBS_PER_PAGE)
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('user_clubs', kwargs={'user_id': self.jane.id}) + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_clubs.html')
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), 2)
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())

    def test_user_clubs_view_redirects_to_my_clubs_view_when_queried_user_is_logged_in_user(self):
        """Test if logged in and queried, redirect to my clubs view."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url2, follow=True)
        redirect_url = reverse('club_selector')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club_switcher.html')
        
    def test_user_clubs_view_redirects_to_home_page_when_queried_user_does_not_exist(self):
        """Test redirect to home page when queried user is non-existent"""
        self.client.login(email=self.john.email, password='Password123')
        url = reverse('user_clubs', kwargs={'user_id': 0})
        with self.assertRaisesMessage(User.DoesNotExist, "User matching query does not exist."):
            response = self.client.get(url, follow=True)
            redirect_url = reverse('home')
            self.assertRedirects(response, redirect_url, status_code=404, target_status_code=404)
            self.assertTemplateUsed(response, 'home.html')
        
    def _is_logged_in(self):
        """Testing if logged in."""
        return '_auth_user_id' in self.client.session.keys()

    def _create_test_clubs(self, club_count=10):
        """Creation of clubs."""
        for id in range(1, club_count+1, 1):
            Club.objects.create(
                owner=self.jane,
                name=f'The {id} Book Club',
                location=f'City {id}',
                description=f'Description {id}',
            )
