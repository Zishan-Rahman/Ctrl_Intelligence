from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester, reverse_with_next


class TestUserListView(TestCase, LogInTester):

    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.url = reverse('user_list')
        self.user = User.objects.create(
            first_name="Jim",
            last_name="Doe",
            email="jimdoe@bookclub.com",
            public_bio="I am definitely an abstract concept...",
            favourite_genre="Mystery",
            location="Lancashire",
            age=47,
            password="pbkdf2_sha256$260000$EoTovTO51J1EMhVCgfWM0t$jQjs11u15ELqQDNthGsC+vdLoDJRn2LDjU2qE7KqKj0="
        )

    def test_user_list_url(self):
        self.assertEqual(self.url,'/users/')

    def test_correct_user_list_template(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_list.html")

    def test_get_user_list_with_pagination(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_more_test_users(settings.USERS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('user_list') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('user_list') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('user_list') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(response.context['users']), 7)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())


    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

    def test_get_user_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        
    def _create_more_test_users(self, club_count=10):
        """Adapted from Fathima Jamaal-Deen's club list view test(s).
        
        Her original method was _create_test_clubs."""
        for id in range(1, club_count+1, 1):
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
