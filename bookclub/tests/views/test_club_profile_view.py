from django.conf import settings
from django.shortcuts import redirect
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from bookclub.models import User, Club
from bookclub.tests.helpers import LogInTester , reverse_with_next

"""Tests for Club Profile """

class ClubProfileTest(TestCase , LogInTester):

    fixtures = ['bookclub/tests/fixtures/default_users.json' , 'bookclub/tests/fixtures/default_clubs.json', 'bookclub/tests/fixtures/default_applications.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.bush_club.make_member(self.user)
        self.url = reverse('club_profile', kwargs={'club_id': self.bush_club.id})

    def test_club_profile_url(self):
        self.assertEqual(self.url,f'/club_profile/{self.bush_club.id}/')

    def test_correct_club_profile_template(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_profile.html")

    def test_correct_club_profile_redirects_with_error_message_when_given_id_to_a_club_which_does_not_exist(self):
        self.client.login(email=self.user.email, password="Password123")
        url = reverse('club_profile', kwargs={'club_id': 500})
        redirect_url = reverse('club_list')
        response = self.client.get(url, follow=True)

        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        
        my_messages = list(response.context['messages'])
        self.assertEqual(len(my_messages), 1)
        self.assertEqual(my_messages[0].level, messages.ERROR)
        self.assertEqual(my_messages[0].message, "Club does not exist!")

    def test_get_club_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_club_profile_has_correct_details(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('<img src=', html)
        self.assertIn(f'alt="Gravatar of {self.bush_club.name}" class="rounded-circle profile-image">', html)
        self.assertIn(f'<h3>{self.bush_club.name}</h3>', html)
        self.assertIn(f'<p>{self.bush_club.description}</p>', html)
        self.assertIn(f'<a href="/user_profile/{self.bush_club.owner.id}/" style="text-decoration: none;">', html)
        self.assertIn(f'<h6 class="card-title">{self.bush_club.owner.first_name} {self.bush_club.owner.last_name}</h6>', html)
        self.assertIn(f'</a>', html)
        self.assertIn(f'<h6 class="card-title">{self.bush_club.location}</h6>', html)

    def test_club_profile_view_has_cards(self):
        """Checks for card-specific (NOT club-specific) details in the club profile template."""
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('<div class="card w-100">', html)
        self.assertIn('<div class="card-body">', html)
        self.assertIn('<h6 class="card-title">', html)
        
    def test_club_profile_view_has_apply_button_for_non_member(self):
        self.user2 = User.objects.get(email="janedoe@bookclub.com")
        self.client.login(email=self.user2.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn btn-default" id="apply-button"><span class="btn btn-dark" style="background-color: brown;">Apply</span></button>', html)

    def test_club_profile_view_has_meeting_button_for_club_member(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a class="btn btn-default" href="/club_profile/{self.bush_club.id}/meeting/"><span class="btn btn-dark" style="background-color: brown">Schedule meeting</span></a>', html)
        
    def test_club_profile_view_has_meetings_list_button_for_all_user(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a class="btn btn-default" href="/club_profile/{self.bush_club.id}/meetings"><span class="btn btn-dark" style="background-color: brown">See meeting history</span></a>', html)

    """ Test if the club profile page doesn't have a leave button for a non-member of the club """

    def test_club_profile_view_doesnt_have_a_leave_button_for_non_member(self):
        self.user2 = User.objects.get(email="janedoe@bookclub.com")
        self.client.login(email=self.user2.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertNotIn(f'<button type="submit" class="btn btn-default" id="leave-button"><span class="btn btn-dark" style="background-color: brown;">Leave {self.bush_club.name}</button>', html )

    """Test if the club profile page has a leave button for a member of the club """

    def test_club_profile_view_has_a_leave_button_for_club_member(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn btn-default" id="leave-button"><span class="btn btn-dark" style="background-color: brown;">Leave {self.bush_club.name}</button>', html)

    """Test if the club profile page has a leave button for a organiser of a club """
    def test_club_profile_view_has_a_leave_button_for_club_organiser(self):
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        self.bush_club.make_organiser(self.user3)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn btn-default" id="leave-button"><span class="btn btn-dark" style="background-color: brown;">Leave {self.bush_club.name}</button>', html)
    
    def test_disband_button_not_visible_for_owner(self):
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        self.bush_club.make_owner(self.user3)
        response = self.client.get(self.url)

        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn btn-default" id="leave-button"><span class="btn btn-dark" style="background-color: brown;">Disband { self.bush_club.name }</button>', html)

    def test_disband_button_not_visible_for_member(self):
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        self.assertNotIn(f'<button type="submit" class="btn btn-default" id="leave-button"><span class="btn btn-dark" style="background-color: brown;">Disband { self.bush_club.name }</button>', html)
        self.assertNotIn('Disband', html)

    def test_disband_button_not_visible_for_organiser(self):
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        self.bush_club.make_organiser(self.user3)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        self.assertNotIn(f'<button type="submit" class="btn btn-default" id="leave-button"><span class="btn btn-dark" style="background-color: brown;">Disband { self.bush_club.name }</button>', html)
        self.assertNotIn('Disband', html)

    def test_successful_disband(self):
        self.user3 = User.objects.get(email="joedoe@bookclub.com")
        self.client.login(email=self.user3.email, password='Password123')
        self.bush_club.make_member(self.user3)
        self.bush_club.make_owner(self.user3)
        club_id = self.bush_club.id
        response = self.client.get(self.url+'disband', follow=True)

        redirect_url = reverse('club_selector')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

        my_messages = list(response.context['messages'])
        self.assertEqual(len(my_messages), 1)
        self.assertEqual(my_messages[0].level, messages.SUCCESS)
        self.assertEqual(my_messages[0].message, "Club Disbanded!")

        self.assertFalse(Club.objects.filter(pk=club_id).exists())
        

    def test_club_profile_view_doesnt_have_a_post_button_for_non_member(self):
        self.user2 = User.objects.get(email="janedoe@bookclub.com")
        self.client.login(email=self.user2.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertNotIn(f'<button type="submit" class="btn btn-default" id="post-feed"><span class="btn btn-dark" style="background-color: brown;">Club feed</button>', html )

    

    def test_club_profile_view_has_a_post_button_for_club_member(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn btn-default" id="post-feed"><span class="btn btn-dark" style="background-color: brown;">Club feed</button>', html)

    
        

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()


