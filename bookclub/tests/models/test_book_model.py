from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import Book


class BookModelTestCase(TestCase):
    fixtures = [
        "bookclub/tests/fixtures/default_books.json"
    ]

    def setUp(self):
        self.book_one = Book.objects.get(isbn="12345678910")
        self.book_two = Book.objects.get(isbn="12345678911")

    # isbn tests

    def test_isbn_cannot_be_longer_than_12_characters(self):
        self.book_one.isbn = "a" * 13
        self._assert_book_is_invalid()

    def test_isbn_cannot_be_empty(self):
        self.book_one.isbn = ""
        self._assert_book_is_invalid()

    def test_isbn_must_be_unique(self):
        self.book_one.isbn = self.book_two.isbn
        self._assert_book_is_invalid()

    # book title tests

    def test_title_cannot_be_empty(self):
        self.book_one.title = ""
        self._assert_book_is_invalid()

    # book author tests

    def test_author_name_cannot_be_empty(self):
        self.book_one.author = ""
        self._assert_book_is_invalid()

    # book publisher tests

    def test_publisher_name_cannot_be_empty(self):
        self.book_one.publisher = ""
        self._assert_book_is_invalid()

    # book publisher tests

    def test_publication_year_cannot_be_empty(self):
        self.book_one.pub_year = ""
        self._assert_book_is_invalid()

    def test_publication_year_cannot_be_before_1800(self):
        self.book_one.pub_year = 1799
        self._assert_book_is_invalid()

    def test_publication_year_cannot_be_after_2022(self):
        self.book_one.pub_year = 2023
        self._assert_book_is_invalid()

    # small url tests

    def test_small_url_cannot_be_empty(self):
        self.book_one.small_url = ""
        self._assert_book_is_invalid()

    def test_small_url_must_contain_domain(self):
        self.book_one.small_url = "http://example"
        self._assert_book_is_invalid()

    def test_small_url_must_contain_protocol(self):
        self.book_one.small_url = "example.com"
        self._assert_book_is_invalid()

    # medium url tests

    def test_medium_url_cannot_be_empty(self):
        self.book_one.medium_url = ""
        self._assert_book_is_invalid()

    def test_medium_url_must_contain_domain(self):
        self.book_one.medium_url = "http://example"
        self._assert_book_is_invalid()

    def test_medium_url_must_contain_protocol(self):
        self.book_one.medium_url = "example.com"
        self._assert_book_is_invalid()

    # large url tests

    def test_large_url_cannot_be_empty(self):
        self.book_one.large_url = ""
        self._assert_book_is_invalid()

    def test_large_url_must_contain_domain(self):
        self.book_one.large_url = "http://example"
        self._assert_book_is_invalid()

    def test_large_url_must_contain_protocol(self):
        self.book_one.large_url = "example.com"
        self._assert_book_is_invalid()

    def _assert_book_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.book_one.full_clean()
