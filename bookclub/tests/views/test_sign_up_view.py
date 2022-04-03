"""Unit tests for the Sign Up View"""
from django.test import TestCase
from django.contrib import messages
from django.urls import reverse
from bookclub.forms import SignUpForm
from django.contrib.auth.hashers import check_password
from bookclub.models import User
from bookclub.tests.helpers import LogInTester

class SignUpViewTestCase(TestCase, LogInTester):
    """Test case for the Sign Up View"""

    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.url = reverse('sign_up')

        self.form_input = {
            'first_name': 'Alex',
            'last_name': 'Willows',
            'email': 'alexwillows@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    def test_sign_up_url(self):
        """Testing the sign up url."""
        self.assertEqual(self.url, '/sign_up/')

    def test_sign_up_uses_correct_template(self):
        """Testing if the sign up uses correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'landing_page.html')

    def test_successful_sign_up(self):
        """Testing if user successfully signed up for a Bookwise account."""
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('landing_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        user = User.objects.get(email='alexwillows@example.org')
        self.assertEqual(user.first_name, 'Alex')
        self.assertEqual(user.last_name, 'Willows')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertFalse(user.is_email_verified)
        message_list = list(response.context['messages'])
        self.assertEqual(len(message_list), 1)
        self.assertEqual(message_list[0].level, messages.SUCCESS)
        self.assertEqual(message_list[0].message, "Verification email sent")

    def test_get_sign_up(self):
        """Testing to get sign up form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        forms = response.context['form']
        self.assertTrue(isinstance(forms['signup'], SignUpForm))
        self.assertFalse(forms['signup'].is_bound)

    def test_unsuccessful_sign_up(self):
        """Testing if user unsuccessfully signed up for a Bookwise account."""
        self.form_input['email']='bademailexample.org'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing_page.html')
        forms = response.context['form']
        self.assertTrue(isinstance(forms['signup'], SignUpForm))
        self.assertTrue(forms['signup'].is_bound)
        self.assertFalse(self._is_logged_in())
