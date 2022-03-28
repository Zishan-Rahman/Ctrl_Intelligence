"""Unit tests for the Club model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Club


# Adapted from the Clucker project and Chess club management system

class ClubModelTestCase(TestCase):
    """Tests for the Club model"""
    fixtures = ["bookclub/tests/fixtures/default_clubs.json",
                "bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.user_one = User.objects.get(pk=1)
        self.user_two = User.objects.get(pk=2)
        self.club_bush_house = Club.objects.get(pk=1)
        self.club_somerset_house = Club.objects.get(pk=2)
        self.club_strand_house = Club.objects.get(pk=3)
        self.club_temple_house = Club.objects.get(pk=4)

    def test_name_cannot_be_blank(self):
        self.club_bush_house.name = ''
        self._assert_book_club_is_invalid()

    def test_name_may_contain_48_characters(self):
        self.club_bush_house.name = "a" * 48
        self._assert_book_club_is_valid()

    def test_name_may_not_contain_over_48_characters(self):
        self.club_bush_house.name = "a" * 49
        self._assert_book_club_is_invalid()

    def test_location_cannot_be_blank(self):
        self.club_bush_house.location = ""
        self._assert_book_club_is_invalid()

    def test_name_must_be_unique(self):
        self.club_bush_house.name = self.club_somerset_house.name
        self._assert_book_club_is_invalid()

    def test_location_may_contain_96_characters(self):
        self.club_bush_house.location = "a" * 96
        self._assert_book_club_is_valid()

    def test_location_may_not_contain_over_96_characters(self):
        self.club_bush_house.location = "a" * 97
        self._assert_book_club_is_invalid()

    def test_book_club_location_cannot_be_blank(self):
        self.club_bush_house.location = ""
        self._assert_book_club_is_invalid()

    def test_description_may_contain_512_characters(self):
        self.club_bush_house.description = "a" * 512
        self._assert_book_club_is_valid()

    def test_location_may_not_contain_over_512_characters(self):
        self.club_bush_house.description = "a" * 513
        self._assert_book_club_is_invalid()

    def test_book_club_description_can_be_blank(self):
        self.club_bush_house.description = ""
        self._assert_book_club_is_valid()

    def test_book_club_must_have_owner(self):
        self.club_bush_house.owner = None
        self._assert_book_club_is_invalid()

    def test_book_club_owners(self):
        self.assertEqual(self.club_bush_house.owner.pk, 1)
        self.assertEqual(self.club_somerset_house.owner.pk, 2)
        self.assertEqual(self.club_strand_house.owner.pk, 1)

    def test_club_meeting_types(self):
        self.assertTrue(self.club_bush_house.meeting_online)
        self.assertTrue(self.club_somerset_house.meeting_online)
        self.assertFalse(self.club_strand_house.meeting_online)

    def test_make_member(self):
        self.club_bush_house.make_member(self.user_two)
        self.assertEqual(self.club_bush_house.get_members().get(pk=2), self.user_two)

    def test_make_organiser(self):
        self.club_bush_house.make_member(self.user_two)
        self.club_bush_house.make_organiser(self.user_two)
        self.assertEqual(self.club_bush_house.get_organisers().get(pk=2), self.user_two)

    def test_make_owner(self):
        self.club_bush_house.make_member(self.user_two)
        self.club_bush_house.make_owner(self.user_two)
        self.assertEqual(self.club_bush_house.owner, self.user_two)
        
    def test_remove_member_from_club(self):
        self.club_temple_house.make_member(self.user_one)
        self.assertEqual(self.club_temple_house.get_members().get(pk=1), self.user_one)
        self.club_temple_house.remove_from_club(self.user_one)
        with self.assertRaises(User.DoesNotExist):
            self.club_temple_house.get_members().get(pk=1)

    def test_remove_organiser_from_club(self):
        self.club_temple_house.make_member(self.user_one)
        self.club_temple_house.make_organiser(self.user_one)
        self.assertEqual(self.club_temple_house.user_level(self.user_one), "Organiser")
        self.assertEqual(self.club_temple_house.get_organisers().get(pk=1), self.user_one)
        self.club_temple_house.remove_from_club(self.user_one)
        with self.assertRaises(User.DoesNotExist):
            self.club_temple_house.get_organisers().get(pk=1)

    def _assert_book_club_is_valid(self):
        try:
            self.club_bush_house.full_clean()
        except ValidationError:
            self.fail('Test club should be valid')

    def _assert_book_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club_bush_house.full_clean()

    # testing a couple of Club model methods

    def test_get_description_method(self):
        self.assertEqual(self.club_bush_house.get_description(), "Bush House Official Book Club!")
    
    def test_get_location_method(self):
        self.assertEqual(self.club_bush_house.get_location(), "Strand, London")
        
    def test_check_if_club_organisers_have_owner_privileges(self):
        self.assertEqual(self.club_bush_house.organiser_has_owner_privilege(), "Organiser does not have owner privileges.")
        self.assertEqual(self.club_somerset_house.organiser_has_owner_privilege(), "Organiser has owner privileges.")

    # testing a couple of exceptions raised
    
    def test_cannot_make_organiser_organiser_again(self):
        self.club_bush_house.make_member(self.user_two)
        self.club_bush_house.make_organiser(self.user_two)
        with self.assertRaises(ValueError):
            self.club_bush_house.make_organiser(self.user_two)
            
    def test_cannot_demote_organiser_twice(self):
        self.club_bush_house.make_member(self.user_two)
        self.club_bush_house.make_organiser(self.user_two)
        self.club_bush_house.demote_organiser(self.user_two)
        with self.assertRaises(ValueError):
            self.club_bush_house.demote_organiser(self.user_two)
            
    def test_cannot_remove_non_member_from_club(self):
        self.club_bush_house.make_member(self.user_two)
        self.club_bush_house.remove_from_club(self.user_two)
        with self.assertRaises(ValueError):
            self.club_bush_house.remove_from_club(self.user_two)
            
    def test_club_validity_test_fails_when_club_is_actually_invalid(self):
        self.club_bush_house.description = "a" * 513
        with self.assertRaisesMessage(AssertionError, 'Test club should be valid'):
            self._assert_book_club_is_valid()
            
    def test_club_invalidity_test_fails_when_club_is_actually_valid(self):
        self.club_bush_house.description = "a" * 512
        with self.assertRaisesMessage(AssertionError, 'ValidationError not raised'):
            self._assert_book_club_is_invalid()
            