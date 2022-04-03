"""Unit tests for the Books model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import Book


class BookModelTestCase(TestCase):
    """Test case for the Book model of Bookwise"""

    fixtures = [
    # Some already defined books to use for our application
        "bookclub/tests/fixtures/default_books.json"
    ]

    def setUp(self):
        self.book_one = Book.objects.get(isbn="12345678910")
        self.book_two = Book.objects.get(isbn="12345678911")

    # isbn tests

    def test_book_isbn(self):
        """Test if the books isbn and the value are equal."""
        self.assertEqual(self.book_one.get_isbn(),"12345678910")
        self.assertEqual(self.book_two.get_isbn(),"12345678911")

    def test_isbn_cannot_be_longer_than_12_characters(self):
        """Test if the books isbn exceeds 12 characters it is invalid."""
        self.book_one.isbn = "a" * 13
        self._assert_book_is_invalid()

    def test_isbn_cannot_be_empty(self):
        """Test if the books isbn is empty it is invalid."""
        self.book_one.isbn = ""
        self._assert_book_is_invalid()

    def test_isbn_must_be_unique(self):
        """Test if the books isbn is not unique it is invalid."""
        self.book_one.isbn = self.book_two.isbn
        self._assert_book_is_invalid()

    # book title tests

    def test_book_title(self):
        """Test if the book's titles and the strings are equal."""
        self.assertEqual(self.book_one.__str__(), self.book_one.get_title())
        self.assertEqual(self.book_one.get_title(), "The Book title")
        self.assertEqual(self.book_two.__str__(), self.book_two.get_title())
        self.assertEqual(self.book_two.get_title(), "The Book title2")

    def test_title_cannot_be_empty(self):
        """Test if the book's title is empty it is invalid"""
        self.book_one.title = ""
        self._assert_book_is_invalid()

    # book author tests

    def test_book_author(self):
        """Test if the authors and the strings are equal."""
        self.assertEqual(self.book_one.get_author(), "John Doe")
        self.assertEqual(self.book_two.get_author(), "John Doe")

    def test_author_name_cannot_be_empty(self):
        """Test if the book's author is empty it is invalid"""
        self.book_one.author = ""
        self._assert_book_is_invalid()

    # book publisher tests

    def test_book_publisher(self):
        """Test if the book's publishers and the strings are equal."""
        self.assertEqual(self.book_one.get_pub_company(), "Example Company")
        self.assertEqual(self.book_two.get_pub_company(), "Example Company")

    def test_publisher_name_cannot_be_empty(self):
        """Test if the book's publisher is empty it is invalid"""
        self.book_one.publisher = ""
        self._assert_book_is_invalid()

    # book publication year tests

    def test_book_publication_year(self):
        """Test if the books publication year and the value are equal."""
        self.assertEqual(self.book_one.get_pub_year(), int("2021"))
        self.assertEqual(self.book_two.get_pub_year(), int("2021"))

    def test_publication_year_cannot_be_empty(self):
        """Test if the book's publication is empty, it is invalid"""
        self.book_one.pub_year = ""
        self._assert_book_is_invalid()

    def test_publication_year_cannot_be_before_1800(self):
        """Test if the book's publication is before 1800, it is invalid"""
        self.book_one.pub_year = 1799
        self._assert_book_is_invalid()

    def test_publication_year_cannot_be_after_2022(self):
        """Test if the book's publication is  after 2022, it is invalid"""
        self.book_one.pub_year = 2023
        self._assert_book_is_invalid()

    # small url tests

    def test_book_small_url(self):
        """Test if the books small url and the url are equal."""
        self.assertEqual(self.book_one.get_small_url(), "http://exampleurl.com")
        self.assertEqual(self.book_two.get_small_url(), "http://exampleurl4.com")

    def test_small_url_cannot_be_empty(self):
        """Test if the small url is empty, it is invalid"""
        self.book_one.small_url = ""
        self._assert_book_is_invalid()

    def test_small_url_must_contain_domain(self):
        """Test if the small url lacks a domain, it is invalid"""
        self.book_one.small_url = "http://example"
        self._assert_book_is_invalid()

    def test_small_url_must_contain_protocol(self):
        """Test if the small url lacks a protocol, it is invalid"""
        self.book_one.small_url = "example.com"
        self._assert_book_is_invalid()

    # medium url tests

    def test_book_medium_url(self):
        """Test if the books medium url and the url are equal."""
        self.assertEqual(self.book_one.get_medium_url(), "http://exampleurl2.com")
        self.assertEqual(self.book_two.get_medium_url(), "http://exampleurl5.com")

    def test_medium_url_cannot_be_empty(self):
        """Test if the medium url is empty, it is invalid"""
        self.book_one.medium_url = ""
        self._assert_book_is_invalid()

    def test_medium_url_must_contain_domain(self):
        """Test if the medium url lacks a domain, it is invalid"""
        self.book_one.medium_url = "http://example"
        self._assert_book_is_invalid()

    def test_medium_url_must_contain_protocol(self):
        """Test if the medium url lacks a protocol, it is invalid"""
        self.book_one.medium_url = "example.com"
        self._assert_book_is_invalid()

    # large url tests

    def test_book_large_url(self):
        """Test if the books large url and the url are equal."""
        self.assertEqual(self.book_one.get_large_url(), "http://exampleurl3.com")
        self.assertEqual(self.book_two.get_large_url(), "http://exampleurl6.com")

    def test_large_url_cannot_be_empty(self):
        """Test if the large url is empty, it is invalid"""
        self.book_one.large_url = ""
        self._assert_book_is_invalid()

    def test_large_url_must_contain_domain(self):
        """Test if the large url lacks a domain, it is invalid"""
        self.book_one.large_url = "http://example"
        self._assert_book_is_invalid()

    def test_large_url_must_contain_protocol(self):
        """Test if the large url lacks a protocol, it is invalid"""
        self.book_one.large_url = "example.com"
        self._assert_book_is_invalid()

    def _assert_book_is_invalid(self):
        """Test if book at its present state is invalid"""
        with self.assertRaises(ValidationError):
            self.book_one.full_clean()
