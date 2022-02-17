from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester, reverse_with_next


class TestUserListView(TestCase, LogInTester):

    fixtures = ["bookclub/tests/fixtures/default_users.json"]

    def setUp(self):
        self.url = reverse('user_list')
        self.user = User.objects.get(pk=1)

    def test_user_list_url(self):
        self.assertEqual(self.url, '/users/')

    def test_get_user_list(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.favourite_genre)


    def test_get_user_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
