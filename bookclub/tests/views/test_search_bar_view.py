"""Unit tests for the Search Bar View"""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from bookclub.models import Book, User
from bookclub.tests.helpers import reverse_with_next

class SearchBarViewTest(TestCase):
    """Test case for the Search Bar View"""

    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.url = reverse('search_page')
        self.user = User.objects.get(pk=1)

    def test_search_page_url(self):
        """Testing the search url."""
        self.assertEqual(self.url, '/search/')

    def test_search_bar_uses_correct_template(self):
        """Testing if the search bar uses correct template."""
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_page.html')

    def test_redirect_if_not_logged_in(self):
        """Test if not logged in, redirect to search page."""
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        
    # def test_search_for_something(self):
    #     """Test if searchbar works adequately."""
    #     self.client.login(email=self.user.email, password='Password123')
    #     response = self.client.post(reverse('search_page'), kwargs={'query': 'Alison'})
    #     context = response.context
    #     print(context)
    #     books = context['books']
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'search_page.html')
    #     self.assertQuerysetEqual(books, Book.objects.filter(title__contains='Alison'), transform= lambda x:x)
        
    def test_queryset_filter(self):
        """Testing for working filter feature."""
        response = self.client.get(reverse('login'))
        self.assertQuerysetEqual(Book.objects.all(), Book.objects.filter(title__contains='Harry Potter'), transform= lambda x:x)
