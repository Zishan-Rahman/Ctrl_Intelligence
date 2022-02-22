from django.conf import settings
from django.test import TestCase
from django.urls import reverse
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

    def test_get_club_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_club_profile_has_correct_details(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'alt="Gravatar of {self.bush_club.name}" class="rounded-circle profile-image" >', html)
        self.assertIn(f'<h3>{self.bush_club.name}</h3>', html)
        self.assertIn(f'<p>Owned by <a href="mailto:{self.bush_club.owner.email}">{self.bush_club.owner.first_name} {self.bush_club.owner.last_name}</a> </p>', html)
        self.assertIn(f'<p>{self.bush_club.description}</p>', html)
        self.assertIn(f'<p>{self.bush_club.description}</p>', html)
        self.assertIn(f"<p>We're based in {self.bush_club.location}</p>", html)

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()
