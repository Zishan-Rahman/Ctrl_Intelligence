"""Unit tests for the Log-In Form"""
from django import forms
from django.test import TestCase
from bookclub.forms import LogInForm
from bookclub.models import User


class TestLogInForm(TestCase):
    """Test case for the Log-In Form"""
    def setUp(self):
        self.form_input = {'email': 'johndoe@example.org', 'password': 'Password123'}
        self.user = User.objects.create_user(
            email='johndoe@example.org',
            first_name='John',
            last_name='Doe',
            public_bio='I\'m gonna kick some ass',
            favourite_genre='Romance',
            location='London',
            age=25,
            password='Password123',
        )

    def test_valid_login_form(self):
        """Testing for valid log-in form."""
        form = LogInForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_contains_required_fields(self):
        """Tests if log-in form has necessary fields."""
        form = LogInForm()
        self.assertIn('email', form.fields)
        self.assertIn('password', form.fields)
        password_field = form.fields['password']    #password needs to be obscuted
        self.assertTrue(isinstance(password_field.widget,forms.PasswordInput))  #checks widget used is password input

    def test_form_rejects_blank_email(self):
        """Tests if log-in club form rejects a blank email."""
        self.form_input['email']= ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_password(self):
        """Tests if log-in form rejects a blank password."""
        self.form_input['password'] = ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_incorrect_email(self):
        """Tests if log-in form rejects an incorrect email."""
        self.form_input['email'] = 'ja'
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_incorrect_password(self):
        """Tests if log-in form rejects an incorrect password."""
        self.form_input['password']= 'pwd'
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_can_authenticate_valid_user(self):
        """Tests if log-in form authenticates a valid user."""
        fixture = User.objects.get(email='johndoe@example.org')
        form_input = {'email': 'johndoe@example.org', 'password': 'Password123'}
        form = LogInForm(data=form_input)
        user = form.get_user()
        self.assertEqual(user, fixture)

    def test_invalid_credentials_do_not_authenticate(self):
        """Tests if log-in form refutes invalid credentials."""
        form_input = {'email': 'johndoe@example.org', 'password': 'WrongPassword123'}
        form = LogInForm(data=form_input)
        user = form.get_user()
        self.assertEqual(user, None)

    def test_blank_password_does_not_authenticate(self):
        """Tests if log-in form refutes blank password."""
        form_input = {'email': 'johndoe@example.org', 'password': ''}
        form = LogInForm(data=form_input)
        user = form.get_user()
        self.assertEqual(user, None)

    def test_blank_email_does_not_authenticate(self):
        """Tests if log-in form refutes an blank email."""
        form_input = {'email': '', 'password': 'WrongPassword123'}
        form = LogInForm(data=form_input)
        user = form.get_user()
        self.assertEqual(user, None)
