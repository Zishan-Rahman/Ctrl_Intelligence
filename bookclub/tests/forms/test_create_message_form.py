"""Unit tests for the Create Message Form"""
from django.test import TestCase
from bookclub.forms import MessageForm
from django import forms
from bookclub.models import User, Message


class TestCreateMessageForm(TestCase):
    """Test case for the Create Message Form"""
    def setUp(self):
        self.form_input = {
            'message':'asdasd'
        }

    def test_chat_form_has_necessary_fields(self):
        """Tests if chat form has necessary fields."""
        form = MessageForm()
        self.assertIn('message', form.fields)

    def test_valid_create_chat_form(self):
        """Testing for valid create chat form."""
        form = MessageForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_message(self):
        """Tests if create club form rejects a blank message."""
        self.form_input['message'] = ''
        form = MessageForm(data=self.form_input)
        self.assertFalse(form.is_valid())
