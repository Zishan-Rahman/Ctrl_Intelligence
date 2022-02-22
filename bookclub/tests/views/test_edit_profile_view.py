"""Tests for the profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import UserForm
from bookclub.models import User
from bookclub.tests.helpers import reverse_with_next

class ProfileViewTest(TestCase):
    """Test suite for the profile view."""

    fixtures = [
        'bookclub/tests/fixtures/default_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.url = reverse('edit_profile')
        self.form_input = {
            'first_name': 'John2',
            'last_name': 'Doe2',
            'email': 'johndoe2@bookclub.com',
            'public_bio': 'New public_bio',
            'favourite_genre': 'Science fiction',
            'location': 'London',
            'age': 39
        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/profile/edit/')

    def test_profile_uses_correct_template(self):
        login = self.client.login(email='johndoe@bookclub.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(str(response.context['user']), 'johndoe@bookclub.com')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')

    def test_get_profile(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertEqual(form.instance, self.user)

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccesful_profile_update(self):
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        self.form_input['email'] = 'BAD_email'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'johndoe@bookclub.com')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.public_bio, "Im just an abstract concept!")
        self.assertEqual(self.user.favourite_genre, "Science fiction")
        self.assertEqual(self.user.location, "London")
        self.assertEqual(self.user.age, 39)

    def test_unsuccessful_profile_update_due_to_duplicate_email(self):
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        self.form_input['email'] = 'janedoe@bookclub.com'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'johndoe@bookclub.com')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.public_bio, "Im just an abstract concept!")
        self.assertEqual(self.user.favourite_genre, "Science fiction")
        self.assertEqual(self.user.location, "London")
        self.assertEqual(self.user.age, 39)

    def test_succesful_profile_update(self):
        self.client.login(email='johndoe@bookclub.com', password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'johndoe2@bookclub.com')
        self.assertEqual(self.user.first_name, 'John2')
        self.assertEqual(self.user.last_name, 'Doe2')
        self.assertEqual(self.user.public_bio, 'New public_bio')
        self.assertEqual(self.user.favourite_genre, "Science fiction")
        self.assertEqual(self.user.location, "London")
        self.assertEqual(self.user.age, 39)

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
