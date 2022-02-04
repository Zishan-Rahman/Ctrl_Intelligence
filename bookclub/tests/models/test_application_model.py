from django.forms import ValidationError
from django.test import TestCase
from bookclub.models import *

class ApplicationModelTestCase(TestCase):
    fixtures = [
        "bookclub/tests/fixtures/default_clubs.json",
        "bookclub/tests/fixtures/default_users.json",
    ]

    def setUp(self):
        self.user_one = User.objects.get(pk=1)
        self.user_two = User.objects.get(pk=2)
        self.club_bush_house = Club.objects.get(pk=1)
        self.club_somerset_house = Club.objects.get(pk=2)
        
    def _assert_application_is_valid(self, application: Application) -> None:
        try:
            application.full_clean()
        except ValidationError:
            self.fail("Application is not valid")
            
    def _assert_application_is_invalid(self, application: Application) -> None:
        with self.assertRaises(ValidationError):
            application.full_clean()