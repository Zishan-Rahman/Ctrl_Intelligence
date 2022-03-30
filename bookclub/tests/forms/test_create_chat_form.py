from django.test import TestCase
from bookclub.forms import ChatForm
from django import forms
from bookclub.models import User, Chat


class TestCreateChatForm(TestCase):
    """Unit tests for the create chat form."""
    def setUp(self):
        self.form_input = {
            'email':'janedoe@example.com'
        }
    """Checks if create chat form has necessary fields"""
    def test_chat_form_has_necessary_fields(self):
        form = ChatForm()
        self.assertIn('email', form.fields)

    """Checks if create chat form is valid"""
    def test_valid_create_chat_form(self):
        form = ChatForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    """Checks if create chat form rejects a blank email"""
    def test_form_rejects_blank_email(self):
        self.form_input['email'] = ''
        form = ChatForm(data=self.form_input)
        self.assertFalse(form.is_valid())
