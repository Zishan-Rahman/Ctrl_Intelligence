"""Unit tests of the Promote and Demote View"""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import *
from bookclub.tests.helpers import reverse_with_next
from django.contrib import messages


class PromoteDemoveViewsTestCase(TestCase):
    """Test case for the Promote and Demote Views"""

    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')
        self.sam = User.objects.get(email='samdoe@bookclub.com')

        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.bush_club.make_member(self.jane)
        self.bush_club.make_member(self.sam)
        self.bush_club.make_member(self.joe)
        self.bush_club.make_organiser(self.jane)

    def test_promote_button_visible_for_owner(self):
        """Testing if promote button is visible to owner."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get('/club_profile/1/members')
        html = response.content.decode('utf8')
        self.assertIn('<td><a class="btn btn-outline-success"', html)
        self.assertIn('Promote', html)

    def test_demote_button_visible_for_owner(self):
        """Testing if demote button is visible to owner."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get('/club_profile/1/members')
        html = response.content.decode('utf8')
        self.assertIn('<td><a class="btn btn-outline-dark"', html)
        self.assertIn('Demote', html)

    def test_promote_button_not_visible_for_member(self):
        """Testing if promote button is invisible to member."""
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get('/club_profile/1/members')
        html = response.content.decode('utf8')
        self.assertNotIn('<a class="btn btn-default"', html)
        self.assertNotIn('Promote', html)

    def test_demote_button_not_visible_for_member(self):
        """Testing if demote button is invisible to member."""
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get('/club_profile/1/members')
        html = response.content.decode('utf8')
        self.assertNotIn('<a class="btn btn-default"', html)
        self.assertNotIn('Demote', html)

    def test_promote_button_not_visible_for_organiser(self):
        """Testing if promote button is invisible to organiser."""
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get('/club_profile/1/members')
        html = response.content.decode('utf8')
        self.assertNotIn('<a class="btn btn-default"', html)
        self.assertNotIn('Promote', html)

    def test_demote_button_not_visible_for_organiser(self):
        """Testing if demote button is invisible to organiser."""
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get('/club_profile/1/members')
        html = response.content.decode('utf8')
        self.assertNotIn('<a class="btn btn-default"', html)
        self.assertNotIn('Demote', html)

    def test_successful_promotion(self):
        """Testing for successful promotion of a member in a club."""
        self.client.login(email=self.john.email, password='Password123')
        beforeMemberCount = self.bush_club.get_number_of_members()
        beforeOrganiserCount = self.bush_club.get_number_organisers()
        response = self.client.get('/club_profile/1/members/3/promote', follow=True)
        redirect_url = '/club_profile/1/members'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        afterMemberCount = self.bush_club.get_number_of_members()
        afterOrganiserCount = self.bush_club.get_number_organisers()
        self.assertEqual(beforeMemberCount, afterMemberCount + 1)
        self.assertEqual(beforeOrganiserCount, afterOrganiserCount - 1)

    def test_successful_demotion(self):
        """Testing for successful demotion of an organiser in a club."""
        self.client.login(email=self.john.email, password='Password123')
        beforeMemberCount = self.bush_club.get_number_of_members()
        beforeOrganiserCount = self.bush_club.get_number_organisers()
        response = self.client.get('/club_profile/1/members/2/demote', follow=True)
        redirect_url = '/club_profile/1/members'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        afterMemberCount = self.bush_club.get_number_of_members()
        afterOrganiserCount = self.bush_club.get_number_organisers()
        self.assertEqual(beforeMemberCount, afterMemberCount - 1)
        self.assertEqual(beforeOrganiserCount, afterOrganiserCount + 1)

    def test_unsuccessful_demotion(self):
        """Testing for unsuccessful demotion of an organiser in a club."""
        self.client.login(email=self.joe.email, password='Password123')
        beforeMemberCount = self.bush_club.get_number_of_members()
        beforeOrganiserCount = self.bush_club.get_number_organisers()
        response = self.client.get('/club_profile/1/members/2/demote', follow=True)
        redirect_url = '/club_profile/1/members'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        afterMemberCount = self.bush_club.get_number_of_members()
        afterOrganiserCount = self.bush_club.get_number_organisers()
        self.assertNotEqual(beforeMemberCount, afterMemberCount - 1)
        self.assertNotEqual(beforeOrganiserCount, afterOrganiserCount + 1)
        self.assertEqual(messages_list[0].message,
                         "You do not have authority to do this!")

    def test_unsuccessful_promotion(self):
        """Testing for unsuccessful promotion of a member in a club."""
        self.client.login(email=self.sam.email, password='Password123')
        beforeMemberCount = self.bush_club.get_number_of_members()
        beforeOrganiserCount = self.bush_club.get_number_organisers()
        response = self.client.get('/club_profile/1/members/3/promote', follow=True)
        redirect_url = '/club_profile/1/members'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        afterMemberCount = self.bush_club.get_number_of_members()
        afterOrganiserCount = self.bush_club.get_number_organisers()
        self.assertNotEqual(beforeMemberCount, afterMemberCount + 1)
        self.assertNotEqual(beforeOrganiserCount, afterOrganiserCount - 1)
        self.assertEqual(messages_list[0].message,
                         "You do not have authority to do this!")

    def test_unsuccessful_promotion_of_an_organiser(self):
        """Testing for unsuccessful promotion of an organiser in a club."""
        self.client.login(email=self.john.email, password='Password123')
        beforeMemberCount = self.bush_club.get_number_of_members()
        beforeOrganiserCount = self.bush_club.get_number_organisers()
        response = self.client.get('/club_profile/1/members/2/promote', follow=True)
        redirect_url = '/club_profile/1/members'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        afterMemberCount = self.bush_club.get_number_of_members()
        afterOrganiserCount = self.bush_club.get_number_organisers()
        self.assertNotEqual(beforeMemberCount, afterMemberCount + 1)
        self.assertNotEqual(beforeOrganiserCount, afterOrganiserCount - 1)
        self.assertEqual(messages_list[0].message,
                         "This person is already an organiser!")