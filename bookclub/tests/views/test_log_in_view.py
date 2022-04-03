"""Unit tests for the Log-in View"""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import LogInForm
from bookclub.models import User
from bookclub.tests.helpers import LogInTester, reverse_with_next

class LogInViewTestCase(TestCase, LogInTester):
    """Test case for the Log-in View"""

    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.url = reverse('login')
        self.user = User.objects.get(pk=1)

    def test_login_url(self):
        """Testing the login url."""
        self.assertEqual(self.url, '/login/')

    def test_login_uses_correct_template(self):
        """Testing if the login uses correct template."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing_page.html')

    def test_get_login(self):
        """Testing for login page."""
        response = self.client.get(self.url)       #getting login view
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing_page.html')
        forms = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(forms['login'], LogInForm))
        self.assertFalse(forms['login'].is_bound)             #display data entered again
        self.assertFalse(next)                      #line asserts that the template is rendered without value for next
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_get_login_with_redirect(self):
        """Test if not logged in, redirect to login page."""
        destination_url = reverse('home')
        self.url = reverse_with_next('login', destination_url)
        response = self.client.get(self.url)         #getting login view
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing_page.html')
        forms = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(forms['login'], LogInForm))
        self.assertFalse(forms['login'].is_bound)           #display data entered again
        self.assertEqual(next, destination_url)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_unsuccessful_login(self):
        """Testing for unsuccesful login."""
        form_input = {'email': 'johndoe@example.org', 'password': 'WrongPassword123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing_page.html')
        forms = response.context['form']
        self.assertTrue(isinstance(forms['login'], LogInForm))
        self.assertFalse(forms['login'].is_bound)            #display data entered again
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

                                                    #Test for unsuccessful log in: blank email
    def test_login_with_blank_username(self):
        """Test for blank username on login form."""
        form_input = { 'email': '', 'password': 'NoM1yag1Do' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing_page.html')
        forms = response.context['form']
        self.assertTrue(isinstance(forms['login'], LogInForm))
        self.assertFalse(forms['login'].is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_login_with_blank_password(self):
        """Test for blank password on login form."""
        form_input = {'email': 'johndoe@example.org', 'password': ''}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing_page.html')
        forms = response.context['form']
        self.assertTrue(isinstance(forms['login'], LogInForm))
        self.assertFalse(forms['login'].is_bound)               #display data entered again
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_successful_login(self):
        """Testing for successful login."""
        form_input = {'email': self.user.email, 'password': 'Password123'}              #valid credential
        response = self.client.post(self.url, form_input, follow=True)                  #as we want client to follow redirect all the way to follow
        self.assertTrue(self._is_logged_in())
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_successful_login_with_redirect(self):
        """Testing for redirect upon successful login."""
        redirect_url = reverse('home')
        form_input = {'email': self.user.email, 'password': 'Password123', 'next': redirect_url }
        response = self.client.post(self.url, form_input, follow=True)

        self.assertTrue(self._is_logged_in())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_post_login_redirects_when_logged_in(self):
        """Test if not logged in, redirect to post login."""
        self.client.login(email = self.user.email, password = "Password123")
        form_input = {'email': 'wronguser@example.org', 'password': 'WrongPassword123'}#valid credential
        response = self.client.post(self.url, form_input, follow=True)
        redirect_url = reverse('home')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_post_login_with_incorrect_credentials_and_redirect(self):
        """Testing for redirect, upon submition of incorrect login details."""
        redirect_url = reverse('home')
        form_input = { 'email': 'johndoe@example.org', 'password': 'WrongPassword123', 'next': redirect_url }
        response = self.client.post(self.url, form_input)
        next = response.context['next']
        self.assertEqual(next, redirect_url)

    def test_valid_login_by_inactive_user(self):
        """Test for valid login by inactive user."""
        self.user.is_active = False
        self.user.save()
        form_input = {'email': 'johndoe@example.org', 'password': 'Password123'}            #valid credential
        response = self.client.post(self.url, form_input, follow=True)                      #as we want client to follow redirect all the way to follow
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing_page.html')
        forms = response.context['form']
        self.assertTrue(isinstance(forms['login'], LogInForm))
        self.assertFalse(forms['login'].is_bound)                                                #display data entered again
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_valid_login_by_unverified_user(self):
        """Test for valid login by unverified user."""
        self.user.is_email_verified = False
        self.user.save()
        form_input = {'email': 'johndoe@bookclub.com', 'password': 'Password123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing_page.html')
        forms = response.context['form']
        self.assertTrue(isinstance(forms['login'], LogInForm))
        self.assertFalse(forms['login'].is_bound)
        self.assertFalse(self._is_logged_in())
        message_list = list(response.context['messages'])
        self.assertEqual(len(message_list), 1)
        self.assertEqual(message_list[0].level, messages.ERROR)
        self.assertEqual(message_list[0].message, "Email is not verified, please check your inbox")
