"""Unit tests for the Edit Club Form"""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import *
from bookclub.forms import EditClubForm


class TestEditClubForm(TestCase):
    """Test case for the Edit Club Form"""
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

    def test_form_has_necessary_fields(self):
        """Tests if edit club form has necessary fields."""
        form = EditClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('meeting_online', form.fields)

    def test_valid_application_form(self):
        """Testing for valid edit club form."""
        form = EditClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_name(self):
        """Tests if create edit club form rejects a blank name."""
        self.form_input['name'] = ''
        form = EditClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_blank_description(self):
        """Tests if create edit club form rejects a blank description."""
        self.form_input['description'] = ''
        form = EditClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_location(self):
        """Tests if create edit club form rejects a blank location."""
        self.form_input['location'] = ''
        form = EditClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())
