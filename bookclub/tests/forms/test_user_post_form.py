#adapted from clucker

from django.test import TestCase
from bookclub.models import User, UserPost
from bookclub.forms import UserPostForm

class UserPostFormTestCase(TestCase):
    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.user_one = User.objects.get(pk=1)

    def test_valid_post_form(self):
        input = {'text': 'x'*200 }
        form = UserPostForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_post_form(self):
        input = {'text': 'x'*600 }
        form = UserPostForm(data=input)
        self.assertFalse(form.is_valid())
