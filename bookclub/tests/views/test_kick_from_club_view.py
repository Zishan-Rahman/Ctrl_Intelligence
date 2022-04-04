"""Unit tests for the Kick From Club View"""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import *
from bookclub.tests.helpers import reverse_with_next
from django.contrib import messages


class KickFromClubViewTestCase(TestCase):
    """Test case of the Kick From Club View"""

    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')

        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.bush_club.make_member(self.jane)
        self.bush_club.make_member(self.joe)
        self.bush_club.make_organiser(self.jane)

    def test_kick_button_visible_for_owner(self):
        """Test if kick button is visible to owner."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get('/club_profile/1/members')
        html = response.content.decode('utf8')
        self.assertIn('<td><a class="btn btn-outline-dark"', html)
        self.assertIn('Remove', html)

    def test_kick_button_not_visible_for_member(self):
        """Test if kick button is invisible to member."""
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get('/club_profile/1/members')
        html = response.content.decode('utf8')
        self.assertNotIn('<td><a class="btn btn-outline-dark', html)
        self.assertNotIn('Remove', html)

    def test_kick_button_not_visible_for_organiser(self):
        """Test if kick button is invisible to organiser."""
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get('/club_profile/1/members')
        html = response.content.decode('utf8')
        self.assertNotIn('<td><a class="btn btn-outline-dark', html)
        self.assertNotIn('Remove', html)

    def test_successful_member_kick(self):
        """Testing for successful kick of a member from a club."""
        self.client.login(email=self.john.email, password='Password123')
        beforeMemberCount = self.bush_club.get_number_of_members()
        response = self.client.get('/club_profile/1/members/3/kick', follow=True)
        redirect_url = '/club_profile/1/members'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        afterMemberCount = self.bush_club.get_number_of_members()
        self.assertEqual(beforeMemberCount, afterMemberCount + 1)
        self.assertEqual(messages_list[0].message,str(User.objects.all().get(pk=3).get_full_name()) + " has been kicked out!")

    def test_successful_organiser_kick(self):
        """Testing for successful kick of an organiser from a club."""
        self.client.login(email=self.john.email, password='Password123')
        beforeOrganiserCount = self.bush_club.get_number_organisers()
        response = self.client.get('/club_profile/1/members/2/kick', follow=True)
        redirect_url = '/club_profile/1/members'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        afterOrganiserCount = self.bush_club.get_number_organisers()
        self.assertEqual(beforeOrganiserCount, afterOrganiserCount + 1)
        self.assertEqual(messages_list[0].message, str(User.objects.all().get(pk=2).get_full_name()) + " has been kicked out!")

    def test_unsuccessful_member_kick(self):
        """Testing for unsuccessful kick of a member from a club"""
        self.client.login(email=self.jane.email, password='Password123')
        beforeMemberCount = self.bush_club.get_number_of_members()
        response = self.client.get('/club_profile/1/members/3/kick', follow=True)
        redirect_url = '/club_profile/1/members'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        afterMemberCount = self.bush_club.get_number_of_members()
        self.assertNotEqual(beforeMemberCount, afterMemberCount + 1)
        self.assertEqual(messages_list[0].message,
                        "You do not have authority to do this!")