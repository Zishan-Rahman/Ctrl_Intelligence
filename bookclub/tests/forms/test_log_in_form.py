"""Unit tests for the log in form."""
from django import forms
from django.test import TestCase
from bookclub.forms import LogInForm
from bookclub.models import User


class LogInFormTestCase(TestCase):
    """Unit tests for the log in form."""
    def setUp(self):
        self.form_input = {'email': 'sensei@cobrakai.dojo', 'password': 'NoM1yag1Do!'}
        self.user1 = User.objects.create_user(
            email = 'sensei@cobrakai.dojo',
            name = 'Jonny Lawrence',
            personal_statement = 'I\'m gonna kick some ass',
            chess_experience = 'B',
            password = 'NoM1yag1Do!',
            bio = 'STRIKE FIRST - STRIKE HARD - NO MERCY',
        )

    def test_valid_log_in_form(self):
        form = LogInForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_contains_required_fields(self):
        form = LogInForm()
        self.assertIn('email', form.fields)
        self.assertIn('password', form.fields)
        password_field = form.fields['password']#password needs to be obscuted
        self.assertTrue(isinstance(password_field.widget,forms.PasswordInput))#checks widget used is password input

    def test_form_rejects_blank_email(self):
        self.form_input['email']= ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_password(self):
        self.form_input['password']= ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_incorrect_email(self):
        self.form_input['email']= 'ja'
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_incorrect_password(self):
        self.form_input['password']= 'pwd'
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_can_authenticate_valid_user(self):
        fixture = User.objects.get(email='sensei@cobrakai.dojo')
        form_input = {'email': 'sensei@cobrakai.dojo', 'password': 'NoM1yag1Do!'}
        form = LogInForm(data=form_input)
        user = form.get_user()
        self.assertEqual(user, fixture)

    def test_invalid_credentials_do_not_authenticate(self):
        form_input = {'email': 'sensei@cobrakai.dojo', 'password': 'WrongPassword123'}
        form = LogInForm(data=form_input)
        user = form.get_user()
        self.assertEqual(user, None)

    def test_blank_password_does_not_authenticate(self):
        form_input = {'email': 'sensei@cobrakai.dojo', 'password': ''}
        form = LogInForm(data=form_input)
        user = form.get_user()
        self.assertEqual(user, None)

    def test_blank_email_does_not_authenticate(self):
        form_input = {'email': '', 'password': 'WrongPassword123'}
        form = LogInForm(data=form_input)
        user = form.get_user()
        self.assertEqual(user, None)
