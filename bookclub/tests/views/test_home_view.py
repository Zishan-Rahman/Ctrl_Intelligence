"""Unit tests of the Home View."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Rating, RecommendedBook, Post
from bookclub.tests.helpers import reverse_with_next


class HomeViewTestCase(TestCase):
    """Test case for the Home View"""

    fixtures = ['bookclub/tests/fixtures/default_users.json',
                'bookclub/tests/fixtures/default_clubs.json',
                'bookclub/tests/fixtures/default_posts.json']

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.post = Post.objects.get(pk=1)

    def test_home_url(self):
        """Testing the home url."""
        self.assertEqual(self.url, '/home/')

    def test_get_home(self):
        """Testing for home page."""
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_uses_correct_template(self):
        """Testing if home page uses correct template."""
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_home_redirects_when_not_logged_in(self):
        """Test if not logged in, redirect to home page."""
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_home_shows_alert_if_not_enough_books_rated(self):
        """Testing if enough books are not rated, home page does shows alert message."""
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'You need to rate <strong>20 books</strong> to receive personalised recommendations.', html)

    def test_home_shows_alert_if_partial_number_of_books_rated(self):
        """Testing if few books are rated, home page displays an alert."""
        self._create_less_ratings()
        user_ratings_count = Rating.objects.filter(user=self.user).count()
        self.assertEqual(5, user_ratings_count)
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'You have rated\n        \n            <strong>5</strong> books\n        \n        so far', html)

    def test_home_shows_top_books_when_not_enough_books_rated(self):
        """Testing if enough books are not rated, home page still shows popular books."""
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'Our Most Popular Books', html)

    def test_home_still_shows_top_books_when_enough_books_rated(self):
        """Testing if enough books are rated, home page still shows popular books."""
        self.client.login(email=self.user.email, password='Password123')
        self._create_ratings()
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        user_ratings_count = Rating.objects.filter(user=self.user).count()
        self.assertEqual(20, user_ratings_count)
        self.assertIn(f'Our Most Popular Books', html)

    def test_home_still_shows_top_books_when_enough_books_rated(self):
        """Testing if enough books are rated, home page still shows popular books."""
        self.client.login(email=self.user.email, password='Password123')
        self._create_ratings()
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        user_ratings_count = Rating.objects.filter(user=self.user).count()
        self.assertEqual(20, user_ratings_count)
        recommended_books_count = RecommendedBook.objects.filter(user=self.user).count()
        
    def test_refresh_recommendations_redirect(self):
        """Testing if enough books are rated, home page still shows popular books."""
        self.client.login(email=self.user.email, password='Password123')
        self._create_ratings()
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        user_ratings_count = Rating.objects.filter(user=self.user).count()
        self.assertEqual(20, user_ratings_count)
        response = self.client.get(reverse('refresh_recommendations'))

    def test_home_does_not_show_alert_if_enough_books_rated(self):
        """Testing if enough books are rated, home page does not show alert message."""
        response = self.client.get(self.url)
        self._create_ratings()
        user_ratings_count = Rating.objects.filter(user=self.user).count()
        self.assertEqual(20, user_ratings_count)
        self.client.login(email=self.user.email, password='Password123')
        html = response.content.decode('utf8')
        self.assertNotIn(
            f'You need to rate <strong>10 books</strong> to receive personalised recommendations.', html)

    def test_home_shows_recommendations_with_button_when_enough_books_rated(self):
        """Testing for recommendations with a button on home page, if enough books are rated by the user."""
        self.client.login(email=self.user.email, password='Password123')
        self._create_ratings()
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self._create_recommendations()
        user_ratings_count = Rating.objects.filter(user=self.user).count()
        user_recs_count = RecommendedBook.objects.filter(user=self.user).count()
        self.assertEqual(10, user_recs_count)
        self.assertEqual(20, user_ratings_count)
        self.assertIn(f'New Recommendations', html)

    def test_successful_refresh_recommendation(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_ratings()
        self._create_recommendations()
        user_recs_count_before = RecommendedBook.objects.filter(user=self.user).count()
        response = self.client.get(self.url + 'recommender')
        html = response.content.decode('utf8')
        user_recs_count_after = RecommendedBook.objects.filter(user=self.user).count()
        self.assertNotEqual(user_recs_count_before,user_recs_count_after)

    def test_home_view_has_posts(self):
        """Testing for posts on home page."""
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(reverse('home'))
        html = response.content.decode('utf8')
        self.assertIn(f' <p class="card-text fw-bold">This is a Bush House Book Club Post</p>',
                      html)

    def test_successful_update_rating(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_ratings()
        ratingBefore = Rating.objects.get(pk=1).get_rating
        response = self.client.get('book_profile/1/rating')
        html = response.content.decode('utf8')
        ratingAfter = Rating.objects.get(pk=1).get_rating
        self.assertNotEqual(ratingBefore , ratingAfter)

    def _create_ratings(self):
        """Creation of 20 ratings."""
        for i in range(0, 20):
            Rating.objects.create(
                user=self.user,
                isbn=f'12341234123{i}',
                rating=10
            )

    def _create_less_ratings(self):
        """Creation of 5 ratings."""
        for i in range(0, 5):
            Rating.objects.create(
                user=self.user,
                isbn=f'12341234123{i}',
                rating=10
            )

    def _create_recommendations(self):
        """Creation of recommendations."""
        for i in range(0, 10):
            RecommendedBook.objects.create(
                user=self.user,
                isbn=f'0063295619',
            )
