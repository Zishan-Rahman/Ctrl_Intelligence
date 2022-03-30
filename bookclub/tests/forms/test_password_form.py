from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.forms import PasswordForm


class TestPasswordForm(TestCase):
    """Unit tests for the password form."""
    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.form_input = {
            'password': 'Password123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }
    """Checks if password form has necessary fields"""
    def test_form_has_necessary_fields(self):
        form = PasswordForm(user=self.user)
        self.assertIn('password', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)

    """Checks if password uses correct password template"""
    def test_password_uses_correct_template(self):
        login = self.client.login(email='johndoe@bookclub.com', password='Password123')
        response = self.client.get(reverse('password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')

    """Checks if password form is valid """
    def test_valid_form(self):
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertTrue(form.is_valid())

   """Checks if password contains an uppercase character"""
    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())

    """Checks if password contains an lowercase character"""
    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())

    """Checks if password contains a number"""
    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABC'
        self.form_input['password_confirmation'] = 'PasswordABC'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())

    """Checks if new password and password confirmation are identical"""
    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = PasswordForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())

    """Raises attribute error upon finding a blank user"""
    def test_password_form_when_user_is_none_raises_error(self):
        form = PasswordForm(user=None)
        with self.assertRaisesMessage(AttributeError,"'PasswordForm' object has no attribute 'cleaned_data'"):
            form.clean()
