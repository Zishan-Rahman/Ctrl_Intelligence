from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import reverse_with_next


class UserProfileTest(TestCase):
    fixtures = ['bookclub/tests/fixtures/default_users.json',
                'bookclub/tests/fixtures/default_user_posts.json']

    def setUp(self):
        self.john = User.objects.get(pk=1)
        self.jane = User.objects.get(pk=2)
        self.joe = User.objects.get(pk=3)
        self.sam = User.objects.get(pk=4)
        self.url = reverse('profile')

    def test_user_profile_url(self):
        self.assertEqual(self.url, '/profile/')

    def test_user_profile_uses_correct_template(self):
        login = self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile.html')

    def test_get_user_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_user_profile_has_correct_details(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('alt="Gravatar of', html)
        self.assertIn('John Doe', html)
        self.assertIn('johndoe@bookclub.com', html)
        self.assertIn('Science fiction', html)
        self.assertIn('London', html)
        self.assertIn('39', html)
        self.assertIn('Im just an abstract concept!', html)

    def test_user_profile_view_has_feed_view_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a href="/user_profile/1/user_feed/" style="text-decoration: none;">View All</a>', html)

    def test_user_profile_view_displays_correct_message_when_no_posts(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('user_profile', kwargs={'user_id': self.joe.id}))
        html = response.content.decode('utf8')
        self.assertIn(
            f'<p class="text-muted"><strong>{self.joe.first_name} {self.joe.last_name}</strong> does not have any posts</p>',
            html)

    def test_user_profile_view_has_posts(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('user_profile', kwargs={'user_id': self.john.id}))
        html = response.content.decode('utf8')
        self.assertIn(f'<h6 class="card-title text-left"><strong>This is a John Doe Post</strong></h6>',
                      html)

    def test_user_profile_view_does_not_display_other_user_posts(self):
        self.client.login(email=self.sam.email, password='Password123')
        response = self.client.get(reverse('user_profile', kwargs={'user_id': self.john.id}))
        html = response.content.decode('utf8')
        self.assertNotIn(f'<h6 class="card-title text-left"><strong>This is a Jane Doe Post</strong></h6>',
                         html)

    def test_my_user_profile_view_does_not_have_follow_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('user_profile', kwargs={'user_id': self.john.id}))
        html = response.content.decode('utf8')
        self.assertNotIn(
            f'<button class=\'btn btn-lg float-end\' style="padding: 15px; color:white; background-color: royalblue; text-transform:uppercase; font-size: 14px">', html)

    def test_my_user_profile_view_has_edit_profile_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('user_profile', kwargs={'user_id': self.john.id}))
        html = response.content.decode('utf8')
        self.assertIn('Edit Profile', html)

    def test_other_user_profile_view_does_not_have_edit_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('user_profile', kwargs={'user_id': self.sam.id}))
        html = response.content.decode('utf8')
        self.assertNotIn('Edit Profile', html)
