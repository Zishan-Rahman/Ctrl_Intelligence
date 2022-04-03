# adapted from clucker
"""Unit tests for the User Post model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import UserPost, User, Club


class UserPostTest(TestCase):
    """Test case for the User Post model of Bookwise"""

    fixtures = [
        # Some already defined users to use for our application
        "bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user_one = User.objects.get(pk=1)
        self.post = UserPost(
            author=self.user_one,
            text="example",
        )

    def test_valid_post(self):
        """Test if the user post is valid."""
        try:
            self.post.full_clean()
        except ValidationError:
            self.fail("Test post should be valid")

    def test_author_must_not_be_blank(self):
        """Testing if the author is blank, a validation error is raised."""
        self.post.author = None
        with self.assertRaisesMessage(AssertionError, "Test message should be valid"):
            self.test_valid_message()

    def test_text_must_not_be_blank(self):
        """Testing if the text is blank, a validation error is raised."""
        self.post.text = ''
        with self.assertRaisesMessage(AssertionError, "Test message should be valid"):
            self.test_valid_message()

    def test_text_must_not_be_overlong(self):
        """Testing if the text is too long, a validation error is raised."""
        self.post.text = 'x' * 281
        with self.assertRaisesMessage(AssertionError, "Test message should be valid"):
            self.test_valid_message()
