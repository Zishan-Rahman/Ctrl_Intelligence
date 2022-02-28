"""Tests for the password reset view."""
from django.test import TestCase
from django.urls import reverse

class PasswordResetViewTest(TestCase):
    """Test suite for the password view."""

    def setUp(self):
        self.url = reverse('password_reset')

    def test_forgot_password_url(self):
        self.assertEqual(self.url, '/password_reset')

    def test_forgot_password_uses_correct_template(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/password/password_reset.html')
