"""Unit tests for the User model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Club


class UserModelTestCase(TestCase):
    """Test case for the User model of Bookwise"""
    fixtures = [
        # Some already defined clubs and users to use for our application
        "bookclub/tests/fixtures/default_clubs.json",
        "bookclub/tests/fixtures/default_users.json",
    ]

    def setUp(self):
        self.user_one = User.objects.get(pk=1)
        self.user_two = User.objects.get(pk=2)
        self.user_three = User.objects.get(pk=3)
        self.user_four = User.objects.get(pk=4)

        self.user = User.objects.get(email = 'johndoe@bookclub.com')
        self.user2 = User.objects.get(email = 'janedoe@bookclub.com')

    # Tests some user model methods that haven't been covered elsewhere in our testing

    def test_user_model_first_name(self):
        """Testing the first name getter in the User model."""
        self.assertEqual(self.user_one.get_first_name(),"John")

    def test_user_model_last_name(self):
        """Testing the last name getter in the User model."""
        self.assertEqual(self.user_one.get_last_name(),"Doe")

    def test_user_model_location(self):
        """Testing the location getter in the User model."""
        self.assertEqual(self.user_one.get_location(),"London")

    def test_user_model_age(self):
        """Testing the age getter in the User model."""
        self.assertEqual(self.user_one.get_age(),39)
        
    def test_user_model_public_bio(self):
        self.assertEqual(self.user.get_bio(),"Im just an abstract concept!")

    # first name tests
    def test_first_name_must_not_be_blank(self):
        """Test if the first name is blank, it is invalid."""
        self.user_one.first_name = ""
        self._assert_user_is_invalid()

    def test_first_name_may_contain_30_characters(self):
        """Test if the first name is 30 characters, it is valid."""
        self.user_one.first_name = "x" * 30
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_31_characters(self):
        """Test if the first name exceeds 30 characters, it is invalid."""
        self.user_one.first_name = "x" * 31
        self._assert_user_is_invalid()

    # last name tests
    def test_last_name_must_not_be_blank(self):
        """Test if the last name is blank, it is invalid."""
        self.user_one.last_name = ""
        self._assert_user_is_invalid()

    def test_last_name_may_contain_30_characters(self):
        """Test if the last name is 30 characters, it is valid."""
        self.user_one.last_name = "x" * 30
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_31_characters(self):
        """Test if the last name exceeds 30 characters, it is invalid."""
        self.user_one.last_name = "x" * 31
        self._assert_user_is_invalid()

    # bio tests
    def test_valid_user(self):
        """Test if the user is valid"""
        self._assert_user_is_valid()

    def test_bio_must_not_contain_more_than_512_characters(self):
        """Test if the bio exceeds 512 characters, it is invalid."""
        self.user_one.public_bio = "x" * 513
        self._assert_user_is_invalid()

    def test_bio_may_contain_512_characters(self):
        """Test if the bio is 512 characters, it is valid."""
        self.user_one.public_bio = "x" * 512
        self._assert_user_is_valid()

    def test_location_must_not_contain_more_than_96_characters(self):
        """Test if the bio exceeds 96 characters, it is invalid."""
        self.user_one.location = "x" * 97
        self._assert_user_is_invalid()

    def test_location_may_contain_96_characters(self):
        """Test if the bio is 96 characters, it is valid."""
        self.user_one.location = "x" * 96
        self._assert_user_is_valid()

    def test_bio_may_not_be_unique(self):
        """Test if bio is not unique, it is valid"""
        self.user_one.public_bio = self.user_two.public_bio
        self._assert_user_is_valid()

    # email tests
    def test_email_must_contain_at_symbol(self):
        """Test if an email does not contain @ symbol, it is invalid."""
        self.user_one.email = "johndoe.example.org"
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        """Test if an email lacks a domain, it is invalid."""
        self.user_one.email = "johndoe@.org"
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        """Test if an email lacks a domain, it is invalid."""
        self.user_one.email = "johndoe@example"
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        """Test if an email contains more than one @ symbol, it is invalid."""
        self.user_one.email = "johndoe@@example.org"
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        """Test if an email is blank, it is invalid."""
        self.user_one.email = ""
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        """Test if an email does not contain a username, it is invalid."""
        self.user_one.email = "@example.org"
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        """Test if an email is not unique, it is invalid."""
        self.user_one.email = self.user_two.email
        self._assert_user_is_invalid()

    def test_toggle_follow_user(self):
        """Testing the toggle to follow a user feature."""
        john = self.user
        jane = self.user2
        self.assertFalse(john.is_following(jane))
        self.assertFalse(jane.is_following(john))
        john.toggle_follow(jane)
        self.assertTrue(john.is_following(jane))
        self.assertFalse(jane.is_following(john))
        john.toggle_follow(jane)
        self.assertFalse(john.is_following(jane))
        self.assertFalse(jane.is_following(john))

    def test_follow_counters(self):
        """Testing follower count feature."""
        john = self.user
        jane = self.user2
        john.toggle_follow(jane)
        jane.toggle_follow(john)
        self.assertEqual(john.follower_count(), 1 )
        self.assertEqual(john.followee_count(), 1 )
        self.assertEqual(jane.follower_count(), 1 )
        self.assertEqual(jane.followee_count(), 1)

    def test_user_cannot_follow_self(self):
        """Testing users cannot follow themselves."""
        self.user.toggle_follow(self.user)
        self.assertEqual(self.user.follower_count(), 0 )
        self.assertEqual(self.user.followee_count(), 0 )

    def _assert_user_is_valid(self):
        """Test if the user is valid."""
        try:
            self.user_one.full_clean()
        except ValidationError:
            self.fail("Test user should be valid")

    def _assert_user_is_invalid(self):
        """Test if the user is invalid."""
        with self.assertRaises(ValidationError):
            self.user_one.full_clean()

    def test_validity_test_fails_when_user_is_invalid(self):
        self.user_one.email = "johndoe@.org"
        with self.assertRaisesMessage(AssertionError, "Test user should be valid"):
            self._assert_user_is_valid()

    def test_users_have_followers(self):
        john = self.user
        jane = self.user2
        john.toggle_follow(jane)
        jane.toggle_follow(john)
        self.assertEqual(john.followers.all()[0], john.get_users_followers()[0])
        self.assertEqual(jane.followers.all()[0], jane.get_users_followers()[0])
