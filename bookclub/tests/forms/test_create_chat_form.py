"""Unit tests for the sign up form."""
from django.test import TestCase
from bookclub.forms import ChatForm
from django import forms
from bookclub.models import User, Chat


class ChatFormTestCase(TestCase):
    def setUp(self):
        self.form_input = {
            'email':'janedoe@example.com'
        }

    def test_chat_form_has_necessary_fields(self):
        form = ChatForm()
        self.assertIn('email', form.fields)

    def test_valid_create_chat_form(self):
        form = ChatForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_email(self):
        self.form_input['email'] = ''
        form = ChatForm(data=self.form_input)
        self.assertFalse(form.is_valid())

