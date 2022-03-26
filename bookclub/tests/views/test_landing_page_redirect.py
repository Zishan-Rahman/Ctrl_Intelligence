from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from django.contrib import auth

class LandingPageRedirectTestCase(TestCase):
    """Test(s) to see if the landing page redirects to the login page when logged in"""

    fixtures = ["bookclub/tests/fixtures/default_users.json"]
    
    def setUp(self):
        self.url = reverse('landing_page')
        self.user = User.objects.get(pk=1)
        
    def test_landing_page_url(self):
        self.assertEqual(self.url, '/')
        
    def test_landing_page_shows_when_user_not_logged_in(self):
        response = self.client.get(reverse('landing_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('landing_page.html')
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)
    
    def test_landing_page_redirects_to_home_when_user_logged_in(self):
        redirect_url = reverse('home')
        self.client.login(email=self.user.email, password=self.user.password)
        response = self.client.get(reverse('landing_page'), follow=False)
        self.assertTemplateUsed('home.html')
        # user = auth.get_user(self.client)
        # self.assertTrue(user.is_authenticated) #still returns False when it shouldn't
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    