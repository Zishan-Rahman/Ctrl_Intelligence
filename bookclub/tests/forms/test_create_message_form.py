from django.test import TestCase
from bookclub.forms import MessageForm
from django import forms
from bookclub.models import User, Message


class TestCreateMessageForm(TestCase):
    """Unit tests for the create message form."""
    def setUp(self):
        self.form_input = {
            'message':'asdasd'
        }
    """Checks if chat form has necessary fields"""
    def test_chat_form_has_necessary_fields(self):
        form = MessageForm()
        self.assertIn('message', form.fields)

    """Checks if create chat form is valid"""
    def test_valid_create_chat_form(self):
        form = MessageForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    """Checks if create club form rejects a blank message"""
    def test_form_rejects_blank_message(self):
        self.form_input['message'] = ''
        form = MessageForm(data=self.form_input)
        self.assertFalse(form.is_valid())
