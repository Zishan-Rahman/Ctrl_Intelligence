"""Unit tests for the Ratings model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Rating, Book, RecommendedBook


class RecommendedBookModelTestCase(TestCase):
    """Tests for the recommended books model"""
    fixtures = ["bookclub/tests/fixtures/default_users.json",
                "bookclub/tests/fixtures/default_books.json",
                "bookclub/tests/fixtures/default_recommended_book.json"
                ]

    def setUp(self):
        self.john = User.objects.get(pk=1)
        self.jane = User.objects.get(pk=2)
        self.book_1 = Book.objects.get(pk=1)
        self.book_2 = Book.objects.get(pk=2)
        self.rec_book_1 = RecommendedBook.objects.get(pk=1)
        self.rec_book_2 = RecommendedBook.objects.get(pk=2)

    def test_isbn_cannot_be_longer_than_12_characters(self):
        self.rec_book_1.isbn = "a" * 13
        self._assert_rec_book_is_invalid()

    def test_isbn_cannot_be_empty(self):
        self.rec_book_1.isbn = ""
        self._assert_rec_book_is_invalid()

    def test_isbn_cannot_be_none(self):
        self.rec_book_1.isbn = None
        self._assert_rec_book_is_invalid()

    def test_rec_book_must_have_all_fields_simultaneously(self):
        self.assertEqual(self.jane, self.rec_book_2.user)
        self.assertEqual(self.book_2.isbn, self.rec_book_2.isbn)

    def test_rec_book_user_exists(self):
        self.assertEqual(self.rec_book_1.user, self.john)

    def test_rec_book_user_must_exist(self):
        self.rec_book_1.user = None
        self._assert_rec_book_is_invalid()

    def _assert_rec_book_is_valid(self):
        try:
            self.rec_book_1.full_clean()
        except ValidationError:
            self.fail('Test club should be valid')

    def _assert_rec_book_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.rec_book_1.full_clean()
