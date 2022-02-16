from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester

class testUserListView(TestCase, LogInTester):
    def setUp(self):
        self.url = reverse('user_list')
        self.user = User.objects.create(
            first_name = "John",
            last_name = "John",
            public_bio = "hfjdsvsk",
	        email = "johndoe@bookclub.coms",
            date_joined = "2022-09-04 06:00"
        )

    def test_user_list_url(self):
        self.assertEqual(self.url,'/users/')

    def test_get_user_list(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertContains(response, user.first_name)
        self.assertContains(response, user.last_name)
        self.assertContains(response, user.public_bio)
        self.assertContains(response, user.email)
        self.assertContains(response, user.date_joined)


    def test_get_user_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
