"""Unit tests for the Favourite Books View"""
from ast import boolop
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.tests.helpers import LogInTester, reverse_with_next



# Books View test is adapted from the Chess Club project

class FavouriteBooksViewTestCase(TestCase, LogInTester):
    """Test case for the Favourite Books View"""

    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.url = reverse('favourites')
        self.user = User.objects.get(pk=1)

    def test_favourite_book_list_url(self):
        """Testing the favourite books url."""
        self.assertEqual(self.url, '/favourites/')

    def test_correct_favourite_book_list_template(self):
        """Testing if the favourite book list uses correct template."""
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self._is_logged_in()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "favourites.html")

    def test_get_favourite_books_list_redirects_when_not_logged_in(self):
        """Test if not logged in, redirect to my favourites."""
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_favourite_book_list_with_pagination(self):
        """Testing for favourite books list with pagination."""
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_favourite_books(settings.BOOKS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'favourites.html')
        self.assertEqual(len(response.context['books']), settings.BOOKS_PER_PAGE)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('favourites') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'favourites.html')
        self.assertEqual(len(response.context['books']), settings.BOOKS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('favourites') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'favourites.html')
        self.assertEqual(len(response.context['books']), settings.BOOKS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('favourites') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'favourites.html')
        self.assertEqual(len(response.context['books']), 2)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())


    def _is_logged_in(self):
        """Testing if logged in."""
        return '_auth_user_id' in self.client.session.keys()

    def _create_test_favourite_books(self, book_count=10):
        """Creation of favourite books."""
        for id in range(1, book_count+1, 1):
            self.user.favourite_books.add(Book.objects.create(
                isbn=id,
                title=f'{id} Book',
                author=f'user {id}',
                pub_year=2010+id,
                publisher=f'{id} Publisher',
                small_url=f'small{id}@example.org',
                medium_url=f'medium{id}@example.org',
                large_url=f'large{id}@example.org',
            ))
