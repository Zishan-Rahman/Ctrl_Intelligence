# adapted from clucker

from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import UserPost, User, Club


class UserPostTest(TestCase):
    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user_one = User.objects.get(pk=1)
        self.post = UserPost(
            author=self.user_one,
            text="example",
        )

    def test_valid_message(self):
        try:
            self.post.full_clean()
        except ValidationError:
            self.fail("Test message should be valid")

    def test_author_must_not_be_blank(self):
        self.post.author = None
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def test_text_must_not_be_blank(self):
        self.post.text = ''
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def test_text_must_not_be_overlong(self):
        self.post.text = 'x' * 281
        with self.assertRaises(ValidationError):
            self.post.full_clean()
