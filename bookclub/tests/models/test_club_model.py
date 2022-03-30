"""Unit tests for the Club model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Club


# Adapted from the Clucker project and Chess club management system

class ClubModelTestCase(TestCase):
    """Test case for the Club model of Bookwise"""

    fixtures = [
    # Some already defined clubs and users to use for our application
            "bookclub/tests/fixtures/default_clubs.json",
            "bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.user_one = User.objects.get(pk=1)
        self.user_two = User.objects.get(pk=2)
        self.club_bush_house = Club.objects.get(pk=1)
        self.club_somerset_house = Club.objects.get(pk=2)
        self.club_strand_house = Club.objects.get(pk=3)
        self.club_temple_house = Club.objects.get(pk=4)

    def test_name_cannot_be_blank(self):
        """Test if the club name is empty it is invalid"""
        self.club_bush_house.name = ''
        self._assert_book_club_is_invalid()

    def test_name_may_contain_48_characters(self):
        """Test if the club name is 48 characters it is valid"""
        self.club_bush_house.name = "a" * 48
        self._assert_book_club_is_valid()

    def test_name_may_not_contain_over_48_characters(self):
        """Test if the club name exceeds 48 characters it is invalid"""
        self.club_bush_house.name = "a" * 49
        self._assert_book_club_is_invalid()

    def test_name_must_be_unique(self):
        """Test if the club name is unique"""
        self.club_bush_house.name = self.club_somerset_house.name
        self._assert_book_club_is_invalid()

    def test_location_may_contain_96_characters(self):
        """Test if the club location is 96 characters it is valid"""
        self.club_bush_house.location = "a" * 96
        self._assert_book_club_is_valid()

    def test_location_may_not_contain_over_96_characters(self):
        """Test if the club location exceeds 96 characters it is invalid"""
        self.club_bush_house.location = "a" * 97
        self._assert_book_club_is_invalid()

    def test_book_club_location_cannot_be_blank(self):
        """Test if the club location is empty it is invalid"""
        self.club_bush_house.location = ""
        self._assert_book_club_is_invalid()

    def test_description_may_contain_512_characters(self):
        """Test if the club description is 512 characters it is valid"""
        self.club_bush_house.description = "a" * 512
        self._assert_book_club_is_valid()

    def test_location_may_not_contain_over_512_characters(self):
        """Test if the club location exceeds 512 characters it is invalid"""
        self.club_bush_house.description = "a" * 513
        self._assert_book_club_is_invalid()

    def test_book_club_description_can_be_blank(self):
        """Test if the club description is empty it is valid"""
        self.club_bush_house.description = ""
        self._assert_book_club_is_valid()

    def test_book_club_must_have_owner(self):
        """Test if the club owner is none it is invalid"""
        self.club_bush_house.owner = None
        self._assert_book_club_is_invalid()

    def test_book_club_owners(self):
        """Testing the primary key getter in club model"""
        self.assertEqual(self.club_bush_house.owner.pk, 1)
        self.assertEqual(self.club_somerset_house.owner.pk, 2)
        self.assertEqual(self.club_strand_house.owner.pk, 1)

    def test_club_meeting_types(self):
        """Testing the meeting type in the club model"""
        self.assertTrue(self.club_bush_house.meeting_online)
        self.assertTrue(self.club_somerset_house.meeting_online)
        self.assertFalse(self.club_strand_house.meeting_online)

    def test_make_member(self):
        """Testing the make member feature in the club model"""
        self.club_bush_house.make_member(self.user_two)
        self.assertEqual(self.club_bush_house.get_members().get(pk=2), self.user_two)

    def test_make_organiser(self):
        """Testing the make organiser feature in the club model"""
        self.club_bush_house.make_member(self.user_two)
        self.club_bush_house.make_organiser(self.user_two)
        self.assertEqual(self.club_bush_house.get_organisers().get(pk=2), self.user_two)

    def test_make_owner(self):
        """Testing the make owner feature in the club model"""
        self.club_bush_house.make_member(self.user_two)
        self.club_bush_house.make_owner(self.user_two)
        self.assertEqual(self.club_bush_house.owner, self.user_two)

    def test_remove_member_from_club(self):
        """Testing the remove member feature in the club model"""
        self.club_temple_house.make_member(self.user_one)
        self.assertEqual(self.club_temple_house.get_members().get(pk=1), self.user_one)
        self.club_temple_house.remove_from_club(self.user_one)
        with self.assertRaises(User.DoesNotExist):
            self.club_temple_house.get_members().get(pk=1)

    def test_remove_organiser_from_club(self):
        """Testing the remove organiser feature in the club model"""
        self.club_temple_house.make_member(self.user_one)
        self.club_temple_house.make_organiser(self.user_one)
        self.assertEqual(self.club_temple_house.user_level(self.user_one), "Organiser")
        self.assertEqual(self.club_temple_house.get_organisers().get(pk=1), self.user_one)
        self.club_temple_house.remove_from_club(self.user_one)
        with self.assertRaises(User.DoesNotExist):
            self.club_temple_house.get_organisers().get(pk=1)

    def _assert_book_club_is_valid(self):
        """Test if the club is valid"""
        try:
            self.club_bush_house.full_clean()
        except ValidationError:
            self.fail('Test club should be valid')

    def _assert_book_club_is_invalid(self):
        """Test if the club is invalid"""
        with self.assertRaises(ValidationError):
            self.club_bush_house.full_clean()

    # testing a couple of Club model getter methods

    def test_get_description_method(self):
        """Testing the description getter method in the Club model."""
        self.assertEqual(self.club_bush_house.get_description(), "Bush House Official Book Club!")

    def test_get_location_method(self):
        """Testing the location getter method in the Club model."""
        self.assertEqual(self.club_bush_house.get_location(), "Strand, London")

    def test_check_if_club_organisers_have_owner_privileges(self):
        """Test if the organiser has owner privileges."""
        self.assertEqual(self.club_bush_house.organiser_has_owner_privilege(), "Organiser does not have owner privileges.")
        self.assertEqual(self.club_somerset_house.organiser_has_owner_privilege(), "Organiser has owner privileges.")

    # testing a couple of exceptions raised

    def test_cannot_make_organiser_organiser_again(self):
        """Test if organiser is made organiser again, raises Value Error."""
        self.club_bush_house.make_member(self.user_two)
        self.club_bush_house.make_organiser(self.user_two)
        with self.assertRaises(ValueError):
            self.club_bush_house.make_organiser(self.user_two)

    def test_cannot_demote_organiser_twice(self):
        """Test if organiser is demoted twice, raises Value Error."""
        self.club_bush_house.make_member(self.user_two)
        self.club_bush_house.make_organiser(self.user_two)
        self.club_bush_house.demote_organiser(self.user_two)
        with self.assertRaises(ValueError):
            self.club_bush_house.demote_organiser(self.user_two)

    def test_cannot_remove_non_member_from_club(self):
        """Test a non member cannot be removed from club, raises Value Error."""
        self.club_bush_house.make_member(self.user_two)
        self.club_bush_house.remove_from_club(self.user_two)
        with self.assertRaises(ValueError):
            self.club_bush_house.remove_from_club(self.user_two)

    def test_club_validity_test_fails_when_club_is_actually_invalid(self):
        """Testing if validity test fails for an invalid club, raises Assertion Error."""
        self.club_bush_house.description = "a" * 513
        with self.assertRaisesMessage(AssertionError, 'Test club should be valid'):
            self._assert_book_club_is_valid()

    def test_club_invalidity_test_fails_when_club_is_actually_valid(self):
        """Testing if invalidity test fails for an valid club, raises Assertion Error."""
        self.club_bush_house.description = "a" * 512
        with self.assertRaisesMessage(AssertionError, 'ValidationError not raised'):
            self._assert_book_club_is_invalid()
