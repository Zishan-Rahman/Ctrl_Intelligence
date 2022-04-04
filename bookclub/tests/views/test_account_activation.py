from django.test import TestCase
from django.urls import reverse
from bookclub.models import Book, User, Rating
from bookclub.utils import generate_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

class AccountActivationTestCase(TestCase):
    
    fixtures = [
        "bookclub/tests/fixtures/default_users.json",
    ]
    
    def setUp(self) -> None:
        self.user = User.objects.get(email="donnydoe@bookclub.com")
        self.token = generate_token.make_token(self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.id))
        self.url = reverse('activate', kwargs={"uid":self.uid, "token":self.token})
    
    def test_account_activation_url(self):
        self.assertEqual(self.url, f'/activate/{self.uid}/{self.token}')
    
    def test_account_activation(self):
        """Test for whether an account can be safely activated."""
        self._activate_account("landing_page.html")
        
    def test_account_can_only_be_activated_once(self):
        """Test for whether an account can only be activated once."""
        self._activate_account("landing_page.html")
        self._activate_account("reverify_email.html")
        
    def _activate_account(self, template):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)