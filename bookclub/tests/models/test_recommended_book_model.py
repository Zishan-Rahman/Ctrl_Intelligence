"""Unit tests for the Reccomended Books model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Rating, Book, RecommendedBook


class RecommendedBooksModelsTestCase(TestCase):
    """Test case for the Recommended Books model of Bookwise"""

    fixtures = [
        # Some already defined users, books and recommended books to use for our application
        "bookclub/tests/fixtures/default_users.json",
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
        """Test if the isbn exceeds 12 characters, it is invalid."""
        self.rec_book_1.isbn = "a" * 13
        self._assert_rec_book_is_invalid()

    def test_isbn_cannot_be_empty(self):
        """Test if the isbn is empty, it is invalid."""
        self.rec_book_1.isbn = ""
        self._assert_rec_book_is_invalid()

    def test_isbn_cannot_be_none(self):
        """Test if the isbn is none, it is invalid."""
        self.rec_book_1.isbn = None
        self._assert_rec_book_is_invalid()

    def test_rec_book_must_have_all_fields_simultaneously(self):
        """Testing if the recommended book contains all fields."""
        self.assertEqual(self.jane, self.rec_book_2.user)
        self.assertEqual(self.book_2.isbn, self.rec_book_2.isbn)

    def test_rec_book_user_exists(self):
        """Testing if the user exists."""
        self.assertEqual(self.rec_book_1.user, self.john)

    def test_rec_book_user_must_exist(self):
        """Test if the user is none, it is invalid."""
        self.rec_book_1.user = None
        self._assert_rec_book_is_invalid()

    def _assert_rec_book_is_valid(self):
        """Test if the recommended book is valid."""
        try:
            self.rec_book_1.full_clean()
        except ValidationError:
            self.fail('Test club should be valid')

    def _assert_rec_book_is_invalid(self):
        """Test if the recommended book is invalid."""
        with self.assertRaises(ValidationError):
            self.rec_book_1.full_clean()
