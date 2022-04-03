# adapted from clucker
"""Unit tests for the Post model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import Post, User, Club


class PostTest(TestCase):
    """Test case for the Post model of Bookwise"""

    fixtures = [
        # Some already defined users and clubs to use for our application
        "bookclub/tests/fixtures/default_users.json",
        "bookclub/tests/fixtures/default_clubs.json"]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user_one = User.objects.get(pk=1)
        self.club_bush_house = Club.objects.get(pk=1)
        self.post = Post(
            author=self.user_one,
            text="example",
            club=self.club_bush_house
        )

    def test_valid_message(self):
        """Test if the message is valid."""
        try:
            self.post.full_clean()
        except ValidationError:
            self.fail("Test message should be valid")

    def test_author_must_not_be_blank(self):
        """Test if author is blank, asssertion error is raised"""
        self.post.author = None
        with self.assertRaisesMessage(AssertionError, "Test message should be valid"):
            self.test_valid_message()

    def test_text_must_not_be_blank(self):
        """Test if text is blank, asssertion error is raised"""
        self.post.text = ''
        with self.assertRaisesMessage(AssertionError, "Test message should be valid"):
            self.test_valid_message()

    def test_text_must_not_be_overlong(self):
        """Test if text is too long, asssertion error is raised"""
        self.post.text = 'x' * 281
        with self.assertRaisesMessage(AssertionError, "Test message should be valid"):
            self.test_valid_message()

    def test_club_must_not_be_blank(self):
        """Test if club is blank, asssertion error is raised"""
        self.post.club = None
        with self.assertRaises(ValidationError):
            self.post.full_clean()
