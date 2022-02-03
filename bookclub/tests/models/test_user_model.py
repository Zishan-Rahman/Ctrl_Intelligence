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

    # first name tests
    def test_first_name_must_not_be_blank(self):
        self.user_one.first_name = ""
        self._assert_user_is_invalid()

    def test_first_name_may_contain_30_characters(self):
        self.user_one.first_name = "x" * 30
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_31_characters(self):
        self.user_one.first_name = "x" * 31
        self._assert_user_is_invalid()

    # last name tests
    def test_last_name_must_not_be_blank(self):
        self.user_one.last_name = ""
        self._assert_user_is_invalid()

    def test_last_name_may_contain_30_characters(self):
        self.user_one.last_name = "x" * 30
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_31_characters(self):
        self.user_one.last_name = "x" * 31
        self._assert_user_is_invalid()

    # bio tests
    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_bio_must_not_contain_more_than_520_characters(self):
        self.user_one.public_bio = "x" * 521
        self._assert_user_is_invalid()

    def test_bio_may_contain_520_characters(self):
        self.user_one.public_bio = "x" * 520
        self._assert_user_is_valid()

    def test_bio_may_not_be_unique(self):
        self.user_one.public_bio = self.user_two.public_bio
        self._assert_user_is_valid()

    # email tests
    def test_email_must_contain_at_symbol(self):
        self.user_one.email = "johndoe.example.org"
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user_one.email = "johndoe@.org"
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user_one.email = "johndoe@example"
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user_one.email = "johndoe@@example.org"
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.user_one.email = ""
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user_one.email = "@example.org"
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        self.user_one.email = self.user_two.email
        self._assert_user_is_invalid()

    def _assert_user_is_valid(self):
        try:
            self.user_one.full_clean()
        except ValidationError:
            self.fail("Test club should be valid")

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user_one.full_clean()
