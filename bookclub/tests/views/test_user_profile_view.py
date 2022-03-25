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
        self.assertIn('alt="Gravatar of', html)
        self.assertIn('John Doe', html)
        self.assertIn('johndoe@bookclub.com', html)
        self.assertIn('Science fiction', html)
        self.assertIn('London', html)
        self.assertIn('39', html)
        self.assertIn('Im just an abstract concept!', html)
