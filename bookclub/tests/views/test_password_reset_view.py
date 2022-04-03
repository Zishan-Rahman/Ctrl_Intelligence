"""Unit tests for the Password Reset View"""
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User

class PasswordResetViewTest(TestCase):
    """Test case for the Password Reset View"""

    fixtures = [
        'bookclub/tests/fixtures/default_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.url = reverse('password_reset')

    def test_forgot_password_url(self):
        """Testing the passoword reset url."""
        self.assertEqual(self.url, '/password_reset')

    def test_forgot_password_uses_correct_template(self):
        """Testing if forgot password uses correct template."""
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/password/password_reset.html')

    def test_sends_forgot_password_email(self):
        """Testing for forgot password email."""
        self.client.post("/password_reset", {"email": self.user.email})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertEqual(mail.outbox[0].subject, 'Password Reset Requested')

    def test_password_reset_confirm_changes_password(self):
        """Testing if password reset changes password."""
        response = self.client.post(self.url,{'email': self.user.email})
        token = response.context['token']
        uid = response.context['uid']
        password_response = self.client.post(reverse('password_reset_confirm', kwargs={'token':token,'uidb64':uid}), {'new_password1':'pass','new_password2':'pass'})
        self.assertEqual(password_response.status_code, 302)
