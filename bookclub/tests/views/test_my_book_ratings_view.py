""""Tests of the individual applications view."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Rating, Book


class MyBookRatingsViewTestCase(TestCase):
    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_ratings.json', 'bookclub/tests/fixtures/default_books.json']

    def setUp(self):
        self.url = reverse('my_book_ratings')
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.book3 = Book.objects.get(isbn=12345678912)

    def get_response_and_html(self):
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        return response, html

    def test_my_book_ratings_url(self):
        self.assertEqual(self.url, '/my_book_ratings/')

    def test_my_book_ratings_uses_correct_template(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_book_ratings.html')

    def test_single_book_rating_has_correct_details(self):
        self.client.login(email=self.john.email, password="Password123")
        response, html = self.get_response_and_html()
        self.assertNotIn('You do not have any book ratings', html)
        self.assertIn('<td>The Book title</td>', html)
        self.assertIn('<td>John Doe</td>', html)
        self.assertIn('<td>2021</td>', html)
        self.assertIn('<td>5</td>', html)

    def test_multiple_book_rating_has_correct_details(self):
        self.client.login(email=self.john.email, password="Password123")
        response, html = self.get_response_and_html()
        self.assertNotIn('You do not have any book ratings', html)
        self.assertIn('<td>The Book title</td>', html)
        self.assertIn('<td>John Doe</td>', html)
        self.assertIn('<td>2021</td>', html)
        self.assertIn('<td>5</td>', html)
        self.assertIn('<td>The Book title2</td>', html)
        self.assertIn('<td>John Doe</td>', html)
        self.assertIn('<td>2021</td>', html)
        self.assertIn('<td>4</td>', html)

    def test_view_after_rating_creation(self):
        self.client.login(email=self.john.email, password="Password123")
        self.rating = Rating.objects.create(user=self.john, book=self.book3, isbn=self.book3.isbn, rating=7)
        response, html = self.get_response_and_html()
        self.assertNotIn('You do not have any book ratings', html)
        self.assertIn('<td>The Book title3</td>', html)
        self.assertIn('<td>John Doe</td>', html)
        self.assertIn('<td>2021</td>', html)
        self.assertIn('<td>7</td>', html)

    def test_get_my_book_ratings_list_with_pagination(self):
        self.client.login(email=self.john.email, password='Password123')
        self._create_test_my_book_ratings(settings.BOOKS_PER_PAGE * 2 + 3 - 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_book_ratings.html')
        self.assertEqual(len(response.context['ratings']), settings.BOOKS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('my_book_ratings') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_book_ratings.html')
        self.assertEqual(len(response.context['ratings']), settings.BOOKS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('my_book_ratings') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_book_ratings.html')
        self.assertEqual(len(response.context['ratings']), settings.BOOKS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('my_book_ratings') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_book_ratings.html')
        self.assertEqual(len(response.context['ratings']), 4)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())

    def _create_test_my_book_ratings(self, my_ratings_count=10):
        for id in range(1, my_ratings_count + 1, 1):
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
            Rating.objects.create(
                user = self.john,
                book = book,
                isbn = book.isbn,
                rating = id
            )
