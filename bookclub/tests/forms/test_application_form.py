"""Unit tests for the Application form."""
from django import forms
from django.test import TestCase
from bookclub.forms import ApplicationForm
from bookclub.models import Club, User


class TestApplicationForm(TestCase):
    fixtures = ['bookclub/tests/fixtures/default_users.json' , 'bookclub/tests/fixtures/default_clubs.json', 'bookclub/tests/fixtures/default_applications.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.bush_club.make_member(self.user)
        self.form_input = {
            'applicant': self.user,
            'club': self.bush_club
        }

    """checks if application form has necessary fields"""

    def test_application_form_has_necessary_fields(self):
        form = ApplicationForm()
        self.assertIn('applicant', form.fields)
        self.assertIn('club', form.fields)

    """checks if application form is valid """

    def test_valid_application_form(self):
        form = ApplicationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    """checks if application form rejects a blank applicant """

    def test_form_rejects_blank_applicant(self):
        self.form_input['applicant'] = ''
        form = ApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    """checks if application form rejects a blank club """

    def test_form_rejects_blank_club(self):
        self.form_input['club'] = ''
        form = ApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())