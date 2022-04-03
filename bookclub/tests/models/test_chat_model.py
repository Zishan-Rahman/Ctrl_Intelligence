"""Unit tests for the Chat model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import Chat, User


class ChatModelTestCase(TestCase):
    """Test case for the Chat model of Bookwise"""

    fixtures = [
    # Some already defined users and chats to use for our application
        "bookclub/tests/fixtures/default_users.json",
        "bookclub/tests/fixtures/default_chats.json"
    ]

    def setUp(self):
        self.john = User.objects.get(pk=1)
        self.jane = User.objects.get(pk=2)
        self.chat_john_to_jane = Chat.objects.get(pk=1)

    def test_sender_cannot_be_null(self):
        """Test if the sender is null it is invalid"""
        self.chat_john_to_jane.user = None
        self._assert_chat_is_invalid()

    def test_receiver_cannot_be_null(self):
        """Test if the receiver is null it is invalid"""
        self.chat_john_to_jane.receiver = None
        self._assert_chat_is_invalid()

    def _assert_chat_is_invalid(self):
        """Test if chat at its present state is invalid"""
        with self.assertRaises(ValidationError):
            self.chat_john_to_jane.full_clean()
