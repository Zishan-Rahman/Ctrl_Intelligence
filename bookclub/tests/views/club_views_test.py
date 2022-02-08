from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.tests.helpers import LogInTester

# clubs views test is adapted from the chess club project

class ClubsListViewTestCase(TestCase, LogInTester):
    """Tests of the club view."""
    def setUp(self):
        self.url = reverse('clubs_list')
        self.user = User.objects.create(
            first_name = "John",
            last_name = "Doe",
	        email = "johndoe@bookclub.com",
	        bio = "my bio",
            public_bio ="I'm just an abstract concept!",
            favourite_genre = "Science fiction",
            age = 39,
	        password ="pbkdf2_sha256$260000$VEDi9wsMYG6eNVeL8WSPqj$LHEiR2iUkusHCIeiQdWS+xQGC9/CjhhrjEOESMMp+c0=",
	        is_active = true
        )

    def test_clubs_list_url(self):
        self.assertEqual(self.url,'/club_list/')

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()