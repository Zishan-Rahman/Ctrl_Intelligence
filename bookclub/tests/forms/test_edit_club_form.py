from django.test import TestCase
from django.urls import reverse
from bookclub.models import *
from bookclub.forms import EditClubForm


class TestEditClubForm(TestCase):
    """Unit tests for the edit club form."""

    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.form_input = {
            'name': 'Bush House Book Club Remastered',
            'description': 'New description',
            'location': 'Strand, London, England',
            'meeting_online': False,
            'organiser_owner': False
        }
    """Checks if edit club form has necessary fields"""
    def test_form_has_necessary_fields(self):
        form = EditClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('meeting_online', form.fields)

    """Checks if edit club form is valid"""
    def test_valid_application_form(self):
        form = EditClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    """Checks if create edit club form rejects a blank name"""
    def test_form_rejects_blank_name(self):
        self.form_input['name'] = ''
        form = EditClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    """Checks if create edit club form rejects a blank description"""
    def test_form_accepts_blank_description(self):
        self.form_input['description'] = ''
        form = EditClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    """Checks if create edit club form rejects a blank location"""
    def test_form_rejects_blank_location(self):
        self.form_input['location'] = ''
        form = EditClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())
