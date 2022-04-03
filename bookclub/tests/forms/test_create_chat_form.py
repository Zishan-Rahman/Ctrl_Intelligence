"""Unit tests for the Create Chat Form"""
from bookclub.forms import ChatForm
from django import forms
from bookclub.models import User, Chat


class TestCreateChatForm(TestCase):
    """Test case for the Create Chat Form"""
    def setUp(self):
        self.form_input = {
            'email':'janedoe@example.com'
        }

    def test_chat_form_has_necessary_fields(self):
        """Tests if create chat form has necessary fields."""
        form = ChatForm()
        self.assertIn('email', form.fields)

    def test_valid_create_chat_form(self):
        """Testing for valid create chat form."""
        form = ChatForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_email(self):
        """Tests if create chat form rejects a blank email."""
        self.form_input['email'] = ''
        form = ChatForm(data=self.form_input)
        self.assertFalse(form.is_valid())
