from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester, reverse_with_next
from django.contrib import messages


class TestUserListView(TestCase, LogInTester):

    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.url = reverse('user_list')
        self.user = User.objects.get(pk=1)
        self.jane = User.objects.get(pk=2)

    def test_user_list_url(self):
        self.assertEqual(self.url,'/users/')

    def test_correct_user_list_template(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_list.html")

    def test_user_list_view_has_follow_button_when_not_following_user(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn btn-dark" style="background-color: brown">Follow</button>', html)

    def test_user_list_view_has_unfollow_button_when_following_user(self):
        self.client.login(email=self.user.email, password='Password123')
        self.user.followees.add(self.jane)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn btn-dark" style="background-color: brown">Unfollow</button>', html)

    def test_follow_button_works_from_user_list(self):
        self.client.login(email=self.user.email, password='Password123')
        before_followee_count = self.user.followees.count()
        response = self.client.get(f'/users/follow/{self.jane.id}/', follow=True)
        redirect_url = self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        after_followee_count = self.user.followees.count()
        self.assertNotEqual(before_followee_count, after_followee_count)

    def test_unfollow_button_works_from_user_list(self):
        self.client.login(email=self.user.email, password='Password123')
        self.user.followees.add(self.jane)
        before_followee_count = self.user.followees.count()
        response = self.client.get(f'/users/unfollow/{self.jane.id}/', follow=True)
        redirect_url = self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_followee_count = self.user.followees.count()
        self.assertNotEqual(before_followee_count, after_followee_count)



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
        self.assertEqual(len(response.context['users']), 6)
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
        """Adapted from Fathima Jamal-Deen's club list view test(s).

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
