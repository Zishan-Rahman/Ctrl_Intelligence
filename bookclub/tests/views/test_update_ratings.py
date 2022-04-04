from django.test import TestCase
from bookclub.forms import ClubForm
from django.urls import reverse
from bookclub.models import Book, User, Rating

class UpdateRatingsTestCase(TestCase):
    
    fixtures = [
        "bookclub/tests/fixtures/default_users.json",
        "bookclub/tests/fixtures/default_books.json",
        "bookclub/tests/fixtures/default_ratings.json"
    ]
    
    def setUp(self) -> None:
        self.user = User.objects.get(email="johndoe@bookclub.com")
        self.book = Book.objects.get(pk=1)
        self.url = reverse("update_ratings", kwargs={"book_id": self.book.id})
        self.rating = Rating.objects.get(pk=1)
        self.data = {
            "user": 1,
            "book": 1,
            "ratings": 7
        }
    
    def test_update_ratings_url(self):
        self.assertEqual(self.url, f'/book_profile/{self.book.id}/rating')
    
    def test_update_ratings(self):
        """Test for whether ratings are updated through the book profile view."""
        self.client.login(email=self.user.email, password="Password123")
        request = self.client.post(self.url, self.data, follow=True)
        redirect_url = f'/book_profile/{self.book.id}/'
        self.assertRedirects(request, redirect_url, status_code=302, target_status_code=200)
        self.rating = Rating.objects.get(user=self.user, book=self.book)
        self.assertEqual(self.rating.get_rating(), 7)
    