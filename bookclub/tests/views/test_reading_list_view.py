"""Unit tests of the Reading List View"""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import Book, User
from bookclub.tests.helpers import LogInTester, reverse_with_next
from django.contrib import messages

class ReadingListTestCase(TestCase, LogInTester):
    """Test case for the Reading List View"""

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
        self.url = reverse('reading_list', kwargs={'user_id': self.user.id})

    def test_reading_list__url(self):
        """Testing the reading list url."""
        self.assertEqual(self.url, f'/reading_list/{self.user.id}/')

    def test_get_reading_list(self):
        """Testing for reading list page."""
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading_list.html')

    def test_reading_list_uses_correct_template(self):
        """Testing if the reading list uses correct template."""
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading_list.html')

    def test_get_reading_list_redirects_when_not_logged_in(self):
        """Testing if not logged in, redirect to reading list page."""
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_book_profile_in_reading_list_has_correct_details(self):
        """Testing if book profile's reading list has the correct details."""
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<img src="{self.book.medium_url}" alt="a">', html)
        self.assertIn(f'<td>{self.book.title}</td>', html)
        self.assertIn(f'<td>{self.book.author}</td>', html)
        self.assertIn(f'<td>{str(self.book.pub_year)}</td>', html)

    def test_reading_list_has_remove_from_reading_list_button(self):
        """Testing if remove from reading list button shows on reading list."""
        self.client.login(email=self.user.email, password='Password123')
        self.user.currently_reading_books.add(self.book)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<td><button type="submit" class="btn" id="bookwiseGeneralBtn" style="font-size: 20px"><i '
                      f'class="bi bi-bookmarks-fill"></i></button></td>', html)

    def test_remove_from_reading_list_works(self):
        """Testing if remove book from reading list is successful."""
        self.client.login(email=self.user.email, password='Password123')
        self.user.currently_reading_books.add(self.book)
        before_reading_list_count = self.user.currently_reading_books.count()
        response = self.client.get(f'/reading_list/{self.book.id}/remove_book/', follow=True)
        redirect_url = self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_reading_list_count = self.user.currently_reading_books.count()
        self.assertNotEqual(before_reading_list_count, after_reading_list_count)


    def test_get_reading_list_with_pagination(self):
        """Testing for reading list with pagination."""
        self.client.login(email=self.user, password="Password123")
        self._create_test_books(settings.BOOKS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading_list.html')
        self.assertEqual(len(response.context['page_obj']), settings.BOOKS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = self.url + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading_list.html')
        self.assertEqual(len(response.context['page_obj']), settings.BOOKS_PER_PAGE)
        page_two_url = self.url + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading_list.html')
        self.assertEqual(len(response.context['page_obj']), settings.BOOKS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = self.url + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reading_list.html')
        self.assertEqual(len(response.context['page_obj']), 3)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())

    def _create_test_books(self, book_count=10):
        """Creation of books."""
        for id in range(1, book_count+1, 1):
            books = Book.objects.create(
                isbn=id,
                title=f'{id} Book',
                author=f'user {id}',
                pub_year=2010+id,
                publisher=f'{id} Publisher',
                small_url=f'small{id}@example.org',
                medium_url=f'medium{id}@example.org',
                large_url=f'large{id}@example.org',
            )
            self.user.currently_reading_books.add(books)
