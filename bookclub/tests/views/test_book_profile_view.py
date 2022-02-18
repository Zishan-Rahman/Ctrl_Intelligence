from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.tests.helpers import reverse_with_next

class BookProfileTest(TestCase):

    fixtures = ['bookclub/tests/fixtures/default_users.json','bookclub/tests/fixtures/default_books.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.book = Book.objects.get(isbn=12345678910)
        self.url = reverse('book_profile', kwargs={'book_id': self.book.id})

    def test_book_profile_url(self):
        self.assertEqual(self.url,f'/book_profile/{self.book.id}/')

    def test_book_profile_uses_correct_template(self):
        login = self.client.login(email='johndoe@bookclub.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_profile.html')

    def test_get_book_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_book_profile_has_correct_details(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(self.book.medium_url, html)
        self.assertIn(self.book.title, html)
        self.assertIn(self.book.isbn, html)
        self.assertIn(self.book.author, html)
        self.assertIn(str(self.book.pub_year), html)
        self.assertIn(self.book.publisher, html)
