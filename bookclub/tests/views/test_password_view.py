"""Tests for the password view."""
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import PasswordForm
from bookclub.models import User
from bookclub.tests.helpers import reverse_with_next

class PasswordViewTestCase(TestCase):
    """Test suite for the password view."""

    fixtures = [
        'bookclub/tests/fixtures/default_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.url = reverse('password')
        self.form_input = {
            'password': 'Password123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }

    def test_password_url(self):
        self.assertEqual(self.url, '/password/')

    def test_home_uses_correct_template(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')

    def test_get_password(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))

    def test_get_password_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_succesful_password_change(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.user.refresh_from_db()
        is_password_correct = check_password('NewPassword123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_password_change_unsuccesful_without_correct_old_password(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['password'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_password_change_unsuccesful_without_password_confirmation(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['password_confirmation'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)
