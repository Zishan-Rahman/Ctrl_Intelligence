"""Tests of the navbar view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import reverse_with_next


class ClubSwitcherViewTestCase(TestCase):
    """Tests of the navbar view."""

    fixtures = ['bookclub/tests/fixtures/default_users.json',
                'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.john = User.objects.get(pk=1)
        self.jane = User.objects.get(pk=2)
        self.joe = User.objects.get(pk=3)
        self.sam = User.objects.get(pk=4)
        self.bush_house = Club.objects.get(pk=1)
        self.somerset_house = Club.objects.get(pk=2)
        self.strand_club = Club.objects.get(pk=3)
        self.url = reverse('club_selector')
        self.url2 = reverse('club_selector_alt')

    def test_redirect_to_my_clubs(self):
        self.assertEqual(self.url, "/my_clubs/")

    def test_redirect_to_my_clubs_alt(self):
        self.assertEqual(self.url2, "/my_clubs1/")

    def test_my_clubs_uses_correct_template(self):
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_switcher.html')

    def test_my_clubs_alt_uses_correct_template(self):
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_switcher_alt.html')

    def test_get_my_clubs(self):
        self.client.login(email=self.john.email, password="Password123")
        response = self.client.get(reverse("club_selector"))
        self.assertTemplateUsed(response, "club_switcher.html")
        self.client.logout()

    def test_get_my_clubs_alt(self):
        self.client.login(email=self.john.email, password="Password123")
        response = self.client.get(reverse("club_selector_alt"))
        self.assertTemplateUsed(response, "club_switcher_alt.html")
        self.client.logout()

    def test_get_my_clubs_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_my_clubs_alt_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url2)
        response = self.client.get(self.url2)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_user_has_no_clubs(self):
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('club_selector'))
        html = response.content.decode('utf8')
        self.assertNotIn('<p class="card-text text-left">Bush House Official Book Club!</p>', html)
        self.assertNotIn('<p class="card-text text-left">Somerset House Official Book Club!</p>', html)
        self.assertNotIn('<p class="card-text text-left">Strand House Official Book Club!</p>', html)
        self.client.logout()

    def test_user_has_no_clubs_alt_view(self):
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('club_selector_alt'))
        html = response.content.decode('utf8')
        self.assertNotIn('<h5 class="card-title"><strong>Bush House Book Club</strong></h5>', html)
        self.assertNotIn('<h5 class="card-title"><strong>Somerset House Book Club</strong></h5>', html)
        self.assertNotIn('<h5 class="card-title"><strong>Strand House Book Club</strong></h5>', html)
        self.client.logout()

    def test_user_has_one_club(self):
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(reverse('club_selector'))
        html = response.content.decode('utf8')
        self.assertNotIn('<p class="card-text text-left">Bush House Official Book Club!</p>', html)
        self.assertIn('<p class="card-text text-left">Somerset House Official Book Club!</p>', html)
        self.assertNotIn('<p class="card-text text-left">Strand House Official Book Club!</p>', html)
        self.client.logout()

    def test_user_has_one_club_alt_view(self):
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(reverse('club_selector_alt'))
        html = response.content.decode('utf8')
        self.assertNotIn('<h5 class="card-title"><strong>Bush House Book Club</strong></h5>', html)
        self.assertIn('<h5 class="card-title"><strong>Somerset House Book Club</strong></h5>', html)
        self.assertNotIn('<h5 class="card-title"><strong>Strand House Book Club</strong></h5>', html)
        self.client.logout()

    def test_user_has_two_clubs(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('club_selector'))
        html = response.content.decode('utf8')
        self.assertIn('<p class="card-text text-left">Bush House Official Book Club!</p>', html)
        self.assertNotIn('<p class="card-text text-left">Somerset House Official Book Club!</p>', html)
        self.assertIn('<p class="card-text text-left">Strand House Official Book Club!</p>', html)
        self.client.logout()

    def test_user_has_two_clubs_alt_view(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('club_selector_alt'))
        html = response.content.decode('utf8')
        self.assertIn('<h5 class="card-title"><strong>Bush House Book Club</strong></h5>', html)
        self.assertNotIn('<h5 class="card-title"><strong>Somerset House Book Club</strong></h5>', html)
        self.assertIn('<h5 class="card-title"><strong>Strand House Book Club</strong></h5>', html)
        self.client.logout()

    def test_clubs_shows_when_user_made_member(self):
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(reverse('club_selector'))
        html = response.content.decode('utf8')
        self.assertNotIn('<p class="card-text text-left">Bush House Official Book Club!</p>', html)
        self.assertNotIn('<p class="card-text text-left">Somerset House Official Book Club!</p>', html)
        self.assertNotIn('<p class="card-text text-left">Strand House Official Book Club!</p>', html)
        self.bush_house.make_member(self.joe)
        response = self.client.get(reverse('club_selector'))
        html = response.content.decode('utf8')
        self.assertIn('<p class="card-text text-left">Bush House Official Book Club!</p>', html)
        self.assertNotIn('<p class="card-text text-left">Somerset House Official Book Club!</p>', html)
        self.assertNotIn('<p class="card-text text-left">Strand House Official Book Club!</p>', html)
        self.client.logout()
