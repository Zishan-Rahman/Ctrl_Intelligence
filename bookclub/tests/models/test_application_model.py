from django.forms import ValidationError
from django.test import TestCase
from bookclub.models import *

class ApplicationModelTestCase(TestCase):
    fixtures = [
        "bookclub/tests/fixtures/default_clubs.json",
        "bookclub/tests/fixtures/default_users.json",
    ]

    def setUp(self) -> None:
        self.user_one = User.objects.get(pk=1)
        self.club_somerset_house = Club.objects.get(pk=2)
        self.application = Application.objects.create(applicant=self.user_one, club=self.club_somerset_house)
        
    def _assert_application_is_valid(self) -> None:
        try:
            self.application.full_clean()
        except ValidationError:
            self.fail("Application is not valid")
            
    def _assert_application_is_invalid(self) -> None:
        with self.assertRaises(ValidationError):
            self.application.full_clean()
            
    def test_new_application(self) -> None:
        self._assert_application_is_valid
        
    def test_applicant_must_be_present(self) -> None:
        self.application.applicant = None
        self._assert_application_is_invalid
        
    def test_club_must_be_present(self) -> None:
        self.application.club = None
        self._assert_application_is_invalid