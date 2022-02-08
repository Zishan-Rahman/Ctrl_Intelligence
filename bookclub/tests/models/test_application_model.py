from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import *

class ApplicationModelTestCase(TestCase):
    """Test case for the Application model of the Bookclubs application"""

    fixtures = [
        # Some already defined users and book clubs to use for our application
        "bookclub/tests/fixtures/default_clubs.json",
        "bookclub/tests/fixtures/default_users.json",
    ]

    def setUp(self) -> None:
        self.user_one = User.objects.get(pk=1)
        self.user_two = User.objects.get(pk=2)
        self.club_bush_house = Club.objects.get(pk=1)
        self.club_somerset_house = Club.objects.get(pk=2)
        self.application = Application.objects.create(applicant=self.user_one, club=self.club_somerset_house)
        
    def _assert_application_is_valid(self) -> None:
        """Auxiliary method for checking if an application at its present state is valid."""
        try:
            self.application.full_clean()
        except ValidationError:
            self.fail("Application is not valid")
            
    def _assert_application_is_invalid(self) -> None:
        """Auxiliary method for checking if an application at its present state is invalid."""
        with self.assertRaises(ValidationError):
            self.application.full_clean()
            
    def test_new_application(self) -> None:
        """Test if the newly set-up application is valid at the moment."""
        self._assert_application_is_valid
        
    def test_applicant_must_be_present(self) -> None:
        """Test if an application with no applicant is invalid."""
        self.application.applicant = None
        self._assert_application_is_invalid
        
    def test_club_must_be_present(self) -> None:
        """Test if an application with no club to apply to is invalid."""
        self.application.club = None
        self._assert_application_is_invalid
        
    def test_club_owner_cannot_be_applicant(self) -> None:
        """Test if a user cannot apply to their own club."""
        self.application.applicant = self.user_two
        self._assert_application_is_invalid
        
    def test_club_itself_cannot_be_applicant(self) -> None:
        """Test if a club entity cannot apply to another club."""
        with self.assertRaises(ValueError):
            self.application.applicant = self.club_bush_house
            
    def test_user_cannot_be_club(self) -> None:
        """Test if an applicant cannot be a club entity."""
        with self.assertRaises(ValueError):
            self.application.club = self.user_one