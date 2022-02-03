"""Unit tests for the sign up form."""
from django.test import TestCase
from bookclub.forms import SignUpForm
from django import forms
from django.contrib.auth.hashers import check_password
from bookclub.models import User


class TestSignUpForm(TestCase):


    def setUp(self):
        self.club = Club.objects.get(name="TestClubNumber1")

        self.form_input = {
            'first_name': 'Alex',
            'last_name': 'Willows',
            'email': 'alexwillows@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    def test_valid_sign_up_form(self):
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)

    def test_password_same_as_confirmation(self):
        self.form_input['password_confirmation'] = 'WrongPassword'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())
