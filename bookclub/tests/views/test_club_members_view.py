from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import LogInTester, reverse_with_next

class ClubMembersViewTestCase(TestCase, LogInTester):
    """Tests of the club members view."""

    fixtures = ["bookclub/tests/fixtures/default_users.json","bookclub/tests/fixtures/default_clubs.json"]
    
    def setUp(self):
        self.club = Club.objects.get(pk=2)
        self.user = User.objects.get(id=self.club.owner.id)
        self.url = reverse('club_members', kwargs={'club_id':self.club.id})
        
    def test_club_members_url(self):
        self.assertEqual(self.url,f'/club_profile/{self.club.id}/members')

    def test_correct_club_members_list_template(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_members.html")
    
    def test_get_club_members_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_club_members_list_view_shows_club_name(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertTrue(self._is_logged_in)
        html = response.content.decode('utf8')
        self.assertIn(f'<h1>Members of {self.club.name}</h1>', html)
    
    def test_get_club_members_list_with_pagination(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_club_members(settings.USERS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_members.html')
        self.assertEqual(len(response.context['page_obj']), settings.USERS_PER_PAGE)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = self.url + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_members.html')
        self.assertEqual(len(response.context['page_obj']), settings.USERS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = self.url + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_members.html')
        self.assertEqual(len(response.context['page_obj']), settings.USERS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = self.url + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_members.html')
        self.assertEqual(len(response.context['page_obj']), 3)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())
        
    def _create_test_club_members(self, user_count=10):
        for id in range(1, user_count+1, 1):
            self.club.make_member(
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
            )
    
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()