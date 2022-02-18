from django import forms
from django.test import TestCase
from bookclub.forms import ApplicationForm
from bookclub.models import Club, User


class TestApplicationForm(TestCase):
    fixtures = ['bookclub/tests/fixtures/default_applications.json', 'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.bush_club.make_member(self.john)
        self.form_input = {
            'applicant': self.user,
            'club': self.bush_club
        }


    def test_application_form_has_necessary_fields(self):
        form = ApplicationFormForm()
        self.assertIn('applicant', form.fields)
        self.assertIn('club', form.fields)


    def test_valid_application_form(self):
        form = ApplicationForm(data=self.form_input)
        self.assertTrue(form.is_valid())


    def test_form_rejects_blank_applicant(self):
        self.form_input['applicant'] = ''
        form = ApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())


    def test_form_rejects_blank_club(self):
        self.form_input['club'] = ''
        form = ApplicationForm(data=self.form_input)
        self.assertFalse(form.is_valid())