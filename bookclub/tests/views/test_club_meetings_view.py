"""Unit tests for the Club Meetings View"""
import datetime
import time
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import Meeting, User, Club
from bookclub.tests.helpers import LogInTester, reverse_with_next


class ClubMeetingsViewTestCase(TestCase, LogInTester):
    """Test case for the Club Meetings view"""
    """Largely adapted from ClubMembersViewTestCase."""

    fixtures = ["bookclub/tests/fixtures/default_users.json", "bookclub/tests/fixtures/default_clubs.json"]

    def setUp(self):
        self.club = Club.objects.get(pk=2)
        self.bush_club = Club.objects.get(pk=1)
        self.john = User.objects.get(pk=1)
        self.user = User.objects.get(id=self.club.owner.id)
        self.url = reverse('club_meetings', kwargs={'club_id': self.club.id})

    def test_club_meetings_url(self):
        """Testing the club meetings url."""
        self.assertEqual(self.url, f'/club_profile/{self.club.id}/meetings')

    def test_correct_club_meetings_list_template(self):
        """Testing if the club meetings list uses correct template."""
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_meetings.html")

    def test_get_club_meetings_list_redirects_when_not_logged_in(self):
        """Test if not logged in, redirect to club meetings."""
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._is_logged_in())

    def test_club_meetings_list_view_contains_meeting_details(self):
        """Test some club meetings' details to see if they actually show up at all."""
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_club_meetings(settings.USERS_PER_PAGE)  # Total: 10 test meetings
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self._is_logged_in())
        self.assertEqual(len(response.context['page_obj']), settings.USERS_PER_PAGE)
        html = response.content.decode('utf8')
        """Test the details of the 10 test meetings created earlier."""
        for i in range(1, settings.USERS_PER_PAGE + 1, 1):
            test_meeting = Meeting.objects.get(id=i)
            self.assertIn(f'<td>May {i}, 2022</td>', html)
            if i != 10:
                self.assertIn(f'<td>12:0{i} p.m.</td>', html)
            else:
                self.assertIn(f'<td>12:{i} p.m.</td>', html)

            self.assertIn(f'{test_meeting.address}</a></td>', html)
            self.assertIn('<a class="btn" href="/club_profile/2/meetings/4/edit" id="bookwiseGeneralBtn" '
                          'style="text-transform: uppercase; font-size: 14px">Edit meeting details</a>', html)

    def test_get_club_meetings_list_with_pagination(self):
        """Testing for clubs meeting list with pagination."""
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_club_meetings(settings.USERS_PER_PAGE * 2 + 3 - 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')
        self.assertEqual(len(response.context['page_obj']), settings.USERS_PER_PAGE)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = self.url + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')
        self.assertEqual(len(response.context['page_obj']), settings.USERS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = self.url + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')
        self.assertEqual(len(response.context['page_obj']), settings.USERS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = self.url + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')
        self.assertEqual(len(response.context['page_obj']), 2)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())
        
    def test_club_meetings_view_redirects_when_club_does_not_exist(self):
        """Testing for redirect to home page when non-existent club queried."""
        self.client.login(email=self.user.email, password='Password123')
        with self.assertRaisesMessage(Club.DoesNotExist, "Club matching query does not exist."):
            response = self.client.get('/club_profile/100000000000/meetings', follow=True)
            redirect_url = reverse('home')
            self.assertRedirects(response, redirect_url, status_code=404, target_status_code=404)
            self.assertTemplateUsed(response, 'home.html')

    def _create_test_club_meetings(self, meeting_count=10):
        """Creation of club meetings."""
        for id in range(1, meeting_count + 1, 1):
            if id % 2 != 0:
                Meeting.objects.create(
                    date=datetime.datetime(2022, 5, id),
                    start_time=datetime.time(12, id),
                    club=self.club,
                    address=f"{id} Melrose Place"
                )
            else:
                Meeting.objects.create(
                    date=datetime.datetime(2022, 5, id),
                    start_time=datetime.time(12, id),
                    club=self.club,
                    address=f"{id} Melrose Place"
                )

    def _is_logged_in(self):
        """Testing if logged in."""
        return '_auth_user_id' in self.client.session.keys()
