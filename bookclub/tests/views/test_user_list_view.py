from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester

class testUserListView(TestCase, LogInTester):
    def setUp(self):
        self.url = reverse('user_list')
        self.user = User.objects.create(
            full_name = "John Doe",
	        email = "johndoe@bookclub.com",
            date_joined = "Feb. 11, 2022, 12:19 a.m."
        )

    def test_user_list_url(self):
        self.assertEqual(self.url,'/user_list/')

    def test_get_user_list(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertContains(response, user.get_full_name)
        self.assertContains(response, user.email)
        self.assertContains(response, user.date_joined)


    def test_get_user_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
