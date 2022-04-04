#adapted from clucker
"""Unit tests for the Post Form"""
from django.test import TestCase
from bookclub.models import User, Post , Club
from bookclub.forms import PostForm


class TestPostForm(TestCase):
    """Test case for the Post Form"""
    fixtures = ["bookclub/tests/fixtures/default_users.json",
                "bookclub/tests/fixtures/default_clubs.json"]

    def setUp(self):
        self.user_one = User.objects.get(pk=1)

    def test_valid_post_form(self):
        """Testing for valid post form."""
        input = {'text': 'x'*200 }
        form = PostForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_post_form(self):
        """Testing for invalid post form."""
        input = {'text': 'x'*600 }
        form = PostForm(data=input)
        self.assertFalse(form.is_valid())
