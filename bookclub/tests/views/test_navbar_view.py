"""Unit tests of the Navbar View."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import reverse_with_next


class NavbarViewTestCase(TestCase):
    """Test case for the Navbar View"""

    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.bush_club.make_member(self.john)

    def test_navbar_displays_search_on_home_page(self):
        """Testing if navbar is displayed on the home page."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'partials/menu.html')
        html = response.content.decode('utf8')
        self.assertIn('<input class="form-control me-2" type="search" placeholder="Search" aria-label="Search" '
                      'name="query" id="search">\n      <button class="btn btn-outline-light" '
                      'type="submit">Search</button>',  html)

    def test_navbar_displays_search_on_clubs_page(self):
        """Testing if navbar is displayed on the clubs page."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('club_list'))
        self.assertTemplateUsed(response, 'partials/menu.html')
        html = response.content.decode('utf8')
        self.assertIn('<input class="form-control me-2" type="search" placeholder="Search" aria-label="Search" '
                      'name="query" id="search">\n      <button class="btn btn-outline-light" '
                      'type="submit">Search</button>',  html)

    def test_navbar_displays_search_on_users_page(self):
        """Testing if navbar is displayed on the users page."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('user_list'))
        self.assertTemplateUsed(response, 'partials/menu.html')
        html = response.content.decode('utf8')
        self.assertIn('<input class="form-control me-2" type="search" placeholder="Search" aria-label="Search" '
                      'name="query" id="search">\n      <button class="btn btn-outline-light" '
                      'type="submit">Search</button>',  html)

    def test_navbar_displays_search_on_books_page(self):
        """Testing if navbar is displayed on books page."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('book_list'))
        self.assertTemplateUsed(response, 'partials/menu.html')
        html = response.content.decode('utf8')
        self.assertIn('<input class="form-control me-2" type="search" placeholder="Search" aria-label="Search" '
                      'name="query" id="search">\n      <button class="btn btn-outline-light" '
                      'type="submit">Search</button>',  html)

    def test_navbar_displays_search_on_edit_profile_page(self):
        """Testing if navbar is displayed on edit profile page."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('profile'))
        self.assertTemplateUsed(response, 'partials/menu.html')
        html = response.content.decode('utf8')
        self.assertIn('<input class="form-control me-2" type="search" placeholder="Search" aria-label="Search" '
                      'name="query" id="search">\n      <button class="btn btn-outline-light" '
                      'type="submit">Search</button>',  html)

    def test_navbar_displays_search_on_edit_password_page(self):
        """Testing if navbar is displayed on edit password page."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('password'))
        self.assertTemplateUsed(response, 'partials/menu.html')
        html = response.content.decode('utf8')
        self.assertIn('<input class="form-control me-2" type="search" placeholder="Search" aria-label="Search" '
                      'name="query" id="search">\n      <button class="btn btn-outline-light" '
                      'type="submit">Search</button>',  html)
