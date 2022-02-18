from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import LogInTester, reverse_with_next


# clubs views test is adapted from the chess club project

class ClubsListViewTestCase(TestCase, LogInTester):
    """Tests of the club view."""

    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.url = reverse('club_list')
        self.user = User.objects.get(pk=1)

    def test_clubs_list_url(self):
        self.assertEqual(self.url, '/clubs/')

    def test_correct_club_list_template(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_list.html")

    def test_get_clubs_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_club_list_with_pagination(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_clubs(settings.CLUBS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('club_list') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('club_list') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('club_list') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertEqual(len(response.context['clubs']), 2)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())


    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

    def _create_test_clubs(self, club_count=10):
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
            Club.objects.create(
                owner_id=id,
                name=f'The {id} Book Club',
                location=f'City {id}',
                description=f'Description {id}',
            )
