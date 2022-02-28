from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from bookclub.models import Book, User
from bookclub.tests.helpers import reverse_with_next

class SearchBarViewTest(TestCase):
    """Test suite for the search bar view"""

    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.url = reverse('search_page')
        self.user = User.objects.get(pk=1)

    def test_search_page_url(self):
        self.assertEqual(self.url, '/search/')

    def test_home_uses_correct_template(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_page.html')

    def test_redirect_if_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_queryset_filter(self):
        response = self.client.get(reverse('log_in'))
        self.assertQuerysetEqual(Book.objects.all(), Book.objects.filter(title__contains='Harry Potter'), transform= lambda x:x)
