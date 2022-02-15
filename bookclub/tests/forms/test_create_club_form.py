"""Unit tests for the sign up form."""
from django.test import TestCase
from bookclub.forms import ClubForm
from django import forms
from bookclub.models import Club, User


class CreateClubTestForm(TestCase):
    def setUp(self):
        self.form_input = {
        'name' : 'BookBusters',
        'description' : 'Crime and Mystery',
        'location' : 'Cardiff',
        'meeting_online' : False
        }

    def test_club_form_has_necessary_fields(self):
        form = ClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('location', form.fields)

    def test_valid_create_club_form(self):
        form = ClubForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_name(self):
        self.form_input['name'] = ''
        form = ClubForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_location(self):
        self.form_input['location'] = ''
        form = ClubForm(data = self.form_input)
        self.assertFalse(form.is_valid())
