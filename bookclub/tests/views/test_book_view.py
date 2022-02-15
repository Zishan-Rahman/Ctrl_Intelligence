from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester


# Books View test is adapted from the Chess Club project

class BooksListViewTestCase(TestCase, LogInTester):
    """Tests of the books view."""

    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.url = reverse('book_list')
        self.user = User.objects.get(pk=1)

    def test_book_list_url(self):
        self.assertEqual(self.url, '/books/')

    def test_correct_book_list_template(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "book_list.html")

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()
