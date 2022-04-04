"""Unit tests for the Transfer Ownership View"""
from django.conf import settings
from django.shortcuts import redirect
from django.test import TestCase
from django.urls import reverse
from bookclub.models import *
from bookclub.tests.helpers import reverse_with_next
from django.contrib import messages
from bookclub.views.club_views import transfer_ownership

class TransferOwnershipViewsTestCase(TestCase):
    """Test case for the Transfer Ownership View"""

    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')
        self.sam = User.objects.get(email='samdoe@bookclub.com')

        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.bush_club.make_member(self.jane)
        self.bush_club.make_member(self.joe)
        self.bush_club.make_member(self.sam)
        self.bush_club.make_organiser(self.jane)

    def test_transfer_owner_button_visible_for_owner(self):
        """Test if transfer owner button is visible for owner."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get('/club_profile/1/members')
        html = response.content.decode('utf8')
        self.assertIn('<td><a class="btn btn-outline-primary"', html)
        self.assertIn('Transfer', html)

    def test_transfer_owner_button_not_visible_for_member(self):
        """Test if transfer owner button is invisible for member."""
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get('/club_profile/1/members')
        html = response.content.decode('utf8')
        self.assertNotIn('<a class="btn btn-default"', html)
        self.assertNotIn('Transfer Ownership', html)

    def test_transfer_owner_button_not_visible_for_organiser(self):
        """Test if transfer owner button is invisible for organiser."""
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get('/club_profile/1/members')
        html = response.content.decode('utf8')
        self.assertNotIn('<a class="btn btn-default"', html)
        self.assertNotIn('Transfer Ownership', html)

    def test_successful_transfer_of_ownership(self):
        """Testing for successful transfer of ownership of a club."""
        self.client.login(email=self.john.email, password="Password123")
        before_owner = self.bush_club.get_owner()
        response = self.client.get(reverse(transfer_ownership, kwargs={'c_pk': self.bush_club.id, 'u_pk': self.jane.id}), follow=True)
        self.bush_club.refresh_from_db()
        redirect_url = f"/club_profile/{self.bush_club.id}/members"
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        after_owner = self.bush_club.get_owner()
        self.assertNotEqual(before_owner, after_owner)

    def test_unsuccessful_transfer_of_ownership(self):
        """Testing for unsuccessful transfer of ownership of a club that isn't owned by the user."""
        self.client.login(email=self.joe.email, password="Password123")
        before_owner = self.joe
        response = self.client.get(reverse(transfer_ownership, kwargs={'c_pk': self.bush_club.id, 'u_pk': self.jane.id}), follow=True)
        self.bush_club.refresh_from_db()
        redirect_url = f"/club_profile/{self.bush_club.id}/members"
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_owner = self.bush_club.get_owner()
        self.assertNotEqual(before_owner, after_owner)
        
    def test_redirect_if_promotion_or_demotion_does_not_exist(self):
        """Test promotion/demotion views redirect if a promotion/demotion doesn't exist."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get('/club_profile/1/members/10000000000000/transfer', follow=True)
        redirect_url = reverse('club_members', kwargs={'club_id':self.bush_club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.client.logout()