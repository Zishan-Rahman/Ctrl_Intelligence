from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import reverse_with_next

class UserProfileTest(TestCase):

    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.url = reverse('profile')

    def test_user_profile_url(self):
        self.assertEqual(self.url,'/profile/')

    def test_user_profile_uses_correct_template(self):
        login = self.client.login(email='johndoe@bookclub.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile.html')

    def test_get_user_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_user_profile_has_correct_details(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('<img src=', html)
        self.assertIn(f'alt="Gravatar of {self.user.first_name } {self.user.last_name}" class="rounded-circle profile-image">', html)
        self.assertIn(f'<h3 class="profile-name">{self.user.first_name} {self.user.last_name}</h3>', html)
        self.assertIn(f'<p class="profile-bio">{self.user.public_bio}</p>', html)
        self.assertIn(f'<p class="profile-email">{self.user.email}</p>', html)
        self.assertIn(f'<p class="profile-genre">Favourite Genre: {self.user.favourite_genre}</p>', html)
        self.assertIn(f'<p class="profile-loc">Location: {self.user.location}</p>', html)
        self.assertIn(f'<p class="profile-age">Age: {self.user.age}</p>', html)
