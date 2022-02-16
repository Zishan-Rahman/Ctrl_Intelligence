"""Unit tests for the Ratings model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import Ratings

class RatingsModelsTestCase(TestCase):
    fixtures = ["bookclub/tests/fixtures/default_ratings.json"]

    def setUp(self):
        self.ratings_one = Ratings.objects.get(pk=1)

    # ratings tests
    def test_ratings_cannot_be_below_0(self):
        self.ratings_one.rating = -1
        self._assert_rating_is_invalid()

    def test_ratings_cannot_be_above_10(self):
        self.ratings_one.rating = 11
        self._assert_rating_is_invalid()

    def test_ratings_may_be_5(self):
        self.ratings_one.rating = 5
        self._assert_rating_is_valid()

    def test_ratings_cannot_be_empty(self):
        self.ratings_one.rating = ""
        self._assert_rating_is_invalid()
