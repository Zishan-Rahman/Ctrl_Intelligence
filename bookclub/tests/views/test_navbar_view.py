# """Tests of the navbar view."""
# from django.test import TestCase
# from django.urls import reverse
# from bookclub.models import User, Club
# from bookclub.tests.helpers import reverse_with_next


# class NavbarViewTestCase(TestCase):
#     """Tests of the navbar view."""

#     fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json']

#     def setUp(self):
#         self.john = User.objects.get(email='johndoe@bookclub.com')
#         self.bush_club = Club.objects.get(name='Bush House Book Club')
#         self.bush_club.make_member(self.john)

#     def test_navbar_displays_books_on_home_page(self):
#         self.client.login(email=self.john.email, password='Password123')
#         response = self.client.get(reverse('home'))
#         self.assertTemplateUsed(response, 'partials/menu.html')
#         html = response.content.decode('utf8')
#         self.assertIn('<li><a class="dropdown-item" href="{% url \'book_list\' %}">View all Books</a></li>',  html)

#     def test_navbar_displays_books_on_clubs_page(self):
#         self.client.login(email=self.john.email, password='Password123')
#         response = self.client.get(reverse('club_list'))
#         self.assertTemplateUsed(response, 'partials/menu.html')
#         html = response.content.decode('utf8')
#         self.assertIn('<li><a class="dropdown-item" href="{% url \'book_list\' %}">View all Books</a></li>',  html)

#     def test_navbar_displays_books_on_users_page(self):
#         self.client.login(email=self.john.email, password='Password123')
#         response = self.client.get(reverse('user_list'))
#         self.assertTemplateUsed(response, 'partials/menu.html')
#         html = response.content.decode('utf8')
#         self.assertIn('<li><a class="dropdown-item" href="{% url \'book_list\' %}">View all Books</a></li>',  html)

#     def test_navbar_displays_books_on_books_page(self):
#         self.client.login(email=self.john.email, password='Password123')
#         response = self.client.get(reverse('book_list'))
#         self.assertTemplateUsed(response, 'partials/menu.html')
#         html = response.content.decode('utf8')
#         self.assertIn('<li><a class="dropdown-item" href="{% url \'book_list\' %}">View all Books</a></li>',  html)

#     def test_navbar_displays_books_on_edit_profile_page(self):
#         self.client.login(email=self.john.email, password='Password123')
#         response = self.client.get(reverse('profile'))
#         self.assertTemplateUsed(response, 'partials/menu.html')
#         html = response.content.decode('utf8')
#         self.assertIn('<li><a class="dropdown-item" href="{% url \'book_list\' %}">View all Books</a></li>',  html)

#     def test_navbar_displays_books_on_edit_password_page(self):
#         self.client.login(email=self.john.email, password='Password123')
#         response = self.client.get(reverse('password'))
#         self.assertTemplateUsed(response, 'partials/menu.html')
#         html = response.content.decode('utf8')
#         self.assertIn('<li><a class="dropdown-item" href="{% url \'book_list\' %}">View all Books</a></li>',  html)

