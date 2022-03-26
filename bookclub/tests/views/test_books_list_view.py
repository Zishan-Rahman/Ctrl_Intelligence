from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.tests.helpers import LogInTester, reverse_with_next
from django.contrib import messages

# Books View test is adapted from the Chess Club project

class BooksListViewTestCase(TestCase, LogInTester):
    """Tests of the club view."""

    fixtures = ["bookclub/tests/fixtures/default_users.json","bookclub/tests/fixtures/default_books.json"]

    def setUp(self):
        self.url = reverse('book_list')
        self.user = User.objects.get(pk=1)
        self.book = Book.objects.get(isbn=12345678910)

    def test_book_list_url(self):
        self.assertEqual(self.url, '/books/')

    def test_correct_book_list_template(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "book_list.html")

    def test_get_books_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_book_list_with_pagination(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_books(settings.BOOKS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
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
        self.assertEqual(len(response.context['books']), 5)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())

    def test_book_list_view_has_remove_from_current_reads_button_when_book_is_in_current_reads(self):
        self.client.login(email=self.user.email, password='Password123')
        self.user.currently_reading_books.add(self.book)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn btn-dark" style="background-color: brown">Remove from My Reading List</button>', html)

    def test_book_list_view_has_add_to_current_reads_button_when_book_is_not_in_current_reads(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn btn-dark" style="background-color: brown">Add to My Reading List</button>', html)

    def test_add_to_current_reads_in_book_list_works(self):
        self.client.login(email=self.user.email, password='Password123')
        before_current_reads_count = self.user.currently_reading_books.count()
        response = self.client.get('/add_to_current_reads_list/1/', follow=True)
        redirect_url = self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        after_current_reads_count = self.user.currently_reading_books.count()
        self.assertNotEqual(before_current_reads_count, after_current_reads_count)

    def test_remove_from_current_reads_in_list_profile_works(self):
        self.client.login(email=self.user.email, password='Password123')
        self.user.currently_reading_books.add(self.book)
        before_current_reads_count = self.user.currently_reading_books.count()
        response = self.client.get('/remove_from_current_reads_list/1/', follow=True)
        redirect_url = self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_current_reads_count = self.user.currently_reading_books.count()
        self.assertNotEqual(before_current_reads_count, after_current_reads_count)

    def test_book_list_has_favourite_button_when_book_is_not_in_favourites(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn btn-dark" style="background-color: brown">Favourite</button>', html)

    def test_book_list_has_unfavourite_button_when_book_is_in_favourites(self):
        self.client.login(email=self.user.email, password='Password123')
        self.user.favourite_books.add(self.book)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn btn-dark" style="background-color: brown">Unfavourite</button>', html)

    def test_favourite_button_in_book_list_works(self):
        self.client.login(email=self.user.email, password='Password123')
        before_current_reads_count = self.user.favourite_books.count()
        response = self.client.get('/book_list/1/favourite', follow=True)
        redirect_url = self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        after_current_reads_count = self.user.favourite_books.count()
        self.assertNotEqual(before_current_reads_count, after_current_reads_count)

    def test_unfavourite_button_in_book_list_works(self):
        self.client.login(email=self.user.email, password='Password123')
        self.user.favourite_books.add(self.book)
        before_current_reads_count = self.user.favourite_books.count()
        response = self.client.get('/book_list/1/unfavourite', follow=True)
        redirect_url = self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_current_reads_count = self.user.favourite_books.count()
        self.assertNotEqual(before_current_reads_count, after_current_reads_count)


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
            Book.objects.create(
                isbn=id,
                title=f'{id} Book',
                author=f'user {id}',
                pub_year=2010+id,
                publisher=f'{id} Publisher',
                small_url=f'small{id}@example.org',
                medium_url=f'medium{id}@example.org',
                large_url=f'large{id}@example.org',
            )
