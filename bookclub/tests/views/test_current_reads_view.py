"""Tests of the current reads view."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import Book, User
from bookclub.tests.helpers import LogInTester, reverse_with_next

class CurrentReadsTestCase(TestCase, LogInTester):
    """Tests of the current reads view."""

    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        id = 1234
        book = Book.objects.create(
            isbn=id,
            title=f'{id} Book',
            author=f'user {id}',
            pub_year=2010+id,
            publisher=f'{id} Publisher',
            small_url=f'small{id}@example.org',
            medium_url=f'medium{id}@example.org',
            large_url=f'large{id}@example.org',
        )
        self.book = book
        self.user.currently_reading_books.add(book)
        self.url = reverse('current_reads', kwargs={'user_id': self.user.id})

    def test_current_reads__url(self):
        self.assertEqual(self.url, f'/current_reads/{self.user.id}/')

    def test_get_current_reads(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading_list.html')

    def test_current_reads_uses_correct_template(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading_list.html')

    def test_get_current_reads_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)


    def test_book_profile_has_correct_details(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<img src="{self.book.medium_url}" alt="a">', html)
        self.assertIn(f'<td>{self.book.title}</td>', html)
        self.assertIn(f'<td>{self.book.author}</td>', html)
        self.assertIn(f'<td>{str(self.book.pub_year)}</td>', html)

    def test_add_to_current_reads_url(self):
        self.assertEqual(self.url, '/current_reads/1/')
