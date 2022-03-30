"""Unit tests for the Message model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import Message, Chat, User


class MessageModelTestCase(TestCase):
    """Test case for the Message model of Bookwise"""

    fixtures = [ # Some already defined users, chats and messages to use for our application
        "bookclub/tests/fixtures/default_users.json",
        "bookclub/tests/fixtures/default_chats.json",
        "bookclub/tests/fixtures/default_messages.json"
    ]

    def setUp(self):
        self.john = User.objects.get(pk=1)
        self.jane = User.objects.get(pk=2)
        self.chat_john_to_jane = Chat.objects.get(pk=1)
        self.first_message = Message.objects.get(pk=1)

    def test_sender_cannot_be_null(self):
        """Test that the sender cannot be null"""
        self.first_message.sender_user = None
        self._assert_message_is_invalid()

    def test_receiver_cannot_be_null(self):
        """Test that the reciever cannot be null"""
        self.first_message.receiver_user = None
        self._assert_message_is_invalid()

    def _assert_message_is_invalid(self):
        """Test if message at its present state is invalid"""
        with self.assertRaises(ValidationError):
            self.first_message.full_clean()
