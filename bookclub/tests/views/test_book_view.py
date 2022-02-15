from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.tests.helpers import LogInTester, reverse_with_next



# Books View test is adapted from the Chess Club project

class BooksListViewTestCase(TestCase, LogInTester):
    """Tests of the books view."""

    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.url = reverse('book_list')
        self.user = User.objects.get(pk=1)

    def test_book_list_url(self):
        self.assertEqual(self.url, '/books/')

    def test_correct_book_list_template(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "book_list.html")

    def test_get_books_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_book_list_with_pagination(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_books(settings.BOOKS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
        print(response.context['books'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_list.html')
        self.assertEqual(len(response.context['books']), settings.BOOKS_PER_PAGE)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('book_list') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_list.html')
        self.assertEqual(len(response.context['books']), settings.BOOKS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('book_list') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_list.html')
        self.assertEqual(len(response.context['books']), settings.BOOKS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('book_list') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_list.html')
        self.assertEqual(len(response.context['books']), 2)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())


    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

    def _create_test_books(self, book_count=10):
        for id in range(1, book_count+1, 1):
            User.objects.create(
                email=f'user{id}@test.org',
                password='Password123',
                first_name=f'First{id}',
                last_name=f'Last{id}',
                public_bio=f'Bio {id}',
                favourite_genre=f'genre {id}',
                location=f'City {id}',
                age=18+id
            )
            a=Book.objects.create(
                isbn=id,
                title=f'{id} Book',
                author=f'user {id}',
                pub_year=2010+id,
                publisher=f'{id} Publisher',
                small_url=f'small{id}@example.org',
                medium_url=f'medium{id}@example.org',
                large_url=f'large{id}@example.org',
            )
            print(a)
