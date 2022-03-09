"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.tests.helpers import reverse_with_next

class CurrentReadsTestCase(TestCase):
    """Tests of the current reads view."""

    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.url = reverse('current_reads')
        self.user = User.objects.get(email='johndoe@bookclub.com')

    def test_current_reads__url(self):
        self.assertEqual(self.url, '/current_reads/')

    def test_get_current_reads(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'current_reads.html')

    def test_current_reads_uses_correct_template(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'current_reads.html')

    def test_get_current_reads_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)


    def test_book_profile_has_correct_details(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<img src="{self.book.medium_url}" alt="a">', html)
        self.assertIn(f'<h3 class="book-title">{self.book.title}</h3>', html)
        self.assertIn(f'<p class="book-author">Author: {self.book.author}</p>', html)
        self.assertIn(f'<p class="book-pub-year">Published Year: {str(self.book.pub_year)}</p>', html)
