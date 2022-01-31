"""Tests of the log out view """
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester

class LogOutViewTestCase(TestCase, LogInTester):
    """Tests of the log out view """

    def setUp(self):
        self.url = reverse('log_out')
        self.user = User.objects.create_user(
            email = 'johndoe@example.org',
            first_name = 'John',
            last_name = 'Doe',
            public_bio = 'I\'m gonna kick some ass',
            favourite_genre = 'Romance',
            location = 'London',
            age = 25,
            password = 'Password123',
        )

    def test_log_out_url(self):
        self.assertEqual(self.url, '/log_out/')

    def test_get_log_out(self):
        self.client.login(email='johndoe@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('landing_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing_page.html')
        self.assertFalse(self._is_logged_in())

    def test_log_out_uses_correct_template(self):
        response = self.client.get(reverse('landing_page'))
        self.assertTemplateUsed(response, 'landing_page.html')

    def test_get_log_out_without_being_logged_in(self):
        response = self.client.get(self.url, follow=True)
        response_url = reverse('landing_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'landing_page.html')
        self.assertFalse(self._is_logged_in())
