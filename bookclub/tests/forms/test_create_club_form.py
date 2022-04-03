"""Unit tests for the Create Club Form"""
from django.test import TestCase
from bookclub.forms import ClubForm
from django import forms
from bookclub.models import Club, User


class TestCreateClubForm(TestCase):
    """Test case for the Create Club Form"""
    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.form_input = {
            'name': 'BookBusters',
            'description': 'Crime and Mystery',
            'location': 'Cardiff',
            'meeting_type': False,
            'organiser_has_owner_privilege': True
        }
        self.owner = User.objects.get(pk=4)


    def test_club_form_has_necessary_fields(self):
        """Tests if create club form has necessary fields."""
        form = ClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('meeting_type', form.fields)
        self.assertIn('organiser_has_owner_privilege', form.fields)

    def test_valid_create_club_form(self):
        """Testing for valid create club form."""
        form = ClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_name(self):
        """Tests if create club form rejects a blank name."""
        self.form_input['name'] = ''
        form = ClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_location(self):
        """Tests if create club form rejects a blank location."""
        self.form_input['location'] = ''
        form = ClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_create_club_form_saves_properly(self):
        """Tests if create club form saves club information well."""
        form = ClubForm(data=self.form_input)
        club = form.save(user=self.owner)
        self.assertEqual(club.name, 'BookBusters')
        self.assertEqual(club.description, 'Crime and Mystery')
        self.assertEqual(club.location, 'Cardiff')
        self.assertEqual(club.owner, self.owner)
        self.assertEqual(club.meeting_online, 'False')
        self.assertEqual(club.organiser_owner, 'True')
