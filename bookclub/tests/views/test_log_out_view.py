"""Unit tests for the Log-out View"""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester

class LogOutViewTestCase(TestCase, LogInTester):
    """Test case for the Log-out View"""

    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.url = reverse('log_out')
        self.user = User.objects.get(pk=1)

    def test_log_out_url(self):
        """Testing the logout url."""
        self.assertEqual(self.url, '/log_out/')

    def test_get_log_out(self):
        """Testing for log out page."""
        self.client.login(email=self.user.email, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('landing_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing_page.html')
        self.assertFalse(self._is_logged_in())

    def test_log_out_uses_correct_template(self):
        """Testing if logout uses correct template."""
        response = self.client.get(reverse('landing_page'))
        self.assertTemplateUsed(response, 'landing_page.html')

    def test_get_log_out_without_being_logged_in(self):
        """Testing for log out page without being logged back in ."""
        response = self.client.get(self.url, follow=True)
        response_url = reverse('landing_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing_page.html')
        self.assertFalse(self._is_logged_in())
