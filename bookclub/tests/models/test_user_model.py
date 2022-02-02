from django.forms import ValidationError
from django.test import TestCase
from bookclub.models import User, Club


class UserModelTestCase(TestCase):
    fixtures = [
        "bookclub/tests/fixtures/default_clubs.json",
        "bookclub/tests/fixtures/default_users.json",
    ]

    def setUp(self):
        self.user_one = User.objects.get(pk=1)
        self.user_two = User.objects.get(pk=2)

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_username_cannot_be_blank(self):
        self.user.username = ""
        self._assert_user_invalid()

    def test_username_can_be_30_characters_long(self):
        self.user.username = "@" + "x" * 29
        self._assert_is_valid()

    def test_username_cannot_be_31_characters_long(self):
        self.user.username = "@" + "x" * 30
        self._assert_is_invalid()

    def test_username_must_start_with_at_symbol(self):
        self.user.username = "johndoe"
        self._assert_user_is_invalid

    def test_username_must_start_with_alphanumericas_after_at(self):
        self.user.username = "@joh!ndoe"
        self._assert_user_is_invalid

    def test_username_must_have_atleast_3_alphanumericals(self):
        self.user.username = "@jo"
        self._assert_user_is_invalid

    def test_username_may_contain_numbers(self):
        self.user.username = "@j0hndoe2"
        self._assert_user_is_valid

    def test_username_must_contain_only_1_at(self):
        self.user.username = "@j@o"
        self._assert_user_is_invalid

    def test_bio_must_not_contain_more_than_520_characters(self):
        self.user.public_bio = "x" * 521
        self._assert_user_is_invalid()

    def test_bio_may_contain_520_characters(self):
        self.user.public_bio = "x" * 520
        self._assert_user_is_valid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = "johndoe.example.org"
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = "johndoe@.org"
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = "johndoe@example"
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = "johndoe@@example.org"
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.user.email = ""
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.email = "@example.org"
        self._assert_user_is_invalid()

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ""
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        second_user = User.objects.get(email="janedoe@bookclub.com")
        self.user.first_name = second_user.first_name
        self._assert_user_is_valid()

    def test_first_name_may_contain_30_characters(self):
        self.user.first_name = "x" * 30
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_31_characters(self):
        self.user.first_name = "x" * 31
        self._assert_user_is_invalid()

    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ""
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        second_user = User.objects.get(email="janedoe@example.org")
        self.user.last_name = second_user.last_name
        self._assert_user_is_valid()

    def test_bio_need_not_be_unique(self):
        second_user = User.objects.get(email="janedoe@bookclub.com")
        self.user.public_bio = second_user.public_bio
        self._assert_user_is_valid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail("Test User should be valid")

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
