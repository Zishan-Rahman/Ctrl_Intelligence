from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import Chat, User


class ChatModelTestCase(TestCase):
    fixtures = [
        "bookclub/tests/fixtures/default_users.json",
        "bookclub/tests/fixtures/default_chats.json"
    ]

    def setUp(self):
        self.john = User.objects.get(pk=1)
        self.jane = User.objects.get(pk=2)
        self.chat_john_to_jane = Chat.objects.get(pk=1)

    def test_sender_cannot_be_null(self):
        self.chat_john_to_jane.user = None
        self._assert_chat_is_invalid()

    def test_receiver_cannot_be_null(self):
        self.chat_john_to_jane.receiver = None
        self._assert_chat_is_invalid()

    def _assert_chat_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.chat_john_to_jane.full_clean()
