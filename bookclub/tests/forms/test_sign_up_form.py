from django.test import TestCase
from bookclub.forms import SignUpForm
from django import forms
from django.contrib.auth.hashers import check_password
from bookclub.models import User


class TestSignUpForm(TestCase):
    """Unit tests for the sign-up form."""

    def setUp(self):

        self.form_input = {
            'first_name': 'Alex',
            'last_name': 'Willows',
            'email': 'alexwillows@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    """Checks if sign-up form is valid"""
    def test_valid_sign_up_form(self):
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    """Checks if sign-up form has necessary fields"""
    def test_form_has_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)

    """Checks if password is the same as confirmation password """
    def test_password_same_as_confirmation(self):
        self.form_input['password_confirmation'] = 'WrongPassword'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())
