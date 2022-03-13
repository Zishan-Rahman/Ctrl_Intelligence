"""Unit tests for the sign up form."""
from django.test import TestCase
from bookclub.forms import MessageForm
from django import forms
from bookclub.models import User, Message


class TestMessageForm(TestCase):
    def setUp(self):
        self.form_input = {
            'message':'asdasd'
        }

    def test_chat_form_has_necessary_fields(self):
        form = MessageForm()
        self.assertIn('message', form.fields)

    def test_valid_create_chat_form(self):
        form = MessageForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_message(self):
        self.form_input['message'] = ''
        form = MessageForm(data=self.form_input)
        self.assertFalse(form.is_valid())

