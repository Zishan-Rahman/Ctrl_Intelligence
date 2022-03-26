"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import reverse_with_next

class HomeViewTestCase(TestCase):
    """Tests of the home view."""

    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.get(email='johndoe@bookclub.com')

    def test_home_url(self):
        self.assertEqual(self.url, '/home/')

    def test_get_home(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_uses_correct_template(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_home_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_home_shows_alert_if_not_enough_books_rated(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('''<div class="container">
      
      <div class="alert alert-warning" role="alert">
        You need to rate 10 books to get better recommendations. You have rated  
        
            no books yet
        
        so far, so click "Browse" then "All Books" or click "Search" on the toolbar to search for books to rate!
      </div>''',html)