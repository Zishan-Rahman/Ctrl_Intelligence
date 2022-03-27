from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import reverse_with_next

class UserProfileTest(TestCase):

    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.url = reverse('user_profile', kwargs={'user_id': self.jane.id})

    def test_user_profile_url(self):
        self.assertEqual(self.url,f'/user_profile/{self.jane.id}/')

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
        self.assertIn('Jane Doe', html)
        self.assertIn('janedoe@bookclub.com', html)
        self.assertIn('Adventure', html)
        self.assertIn('Oxford', html)
        self.assertIn('32', html)
        self.assertIn('Just another fake user', html)

    def test_user_profile_has_following_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button class="link" data-bs-toggle="modal" data-bs-target="#following_modal"><b>{self.jane.followee_count()}</b> Following</button>', html)

    def test_view_profile_has_followers_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button class="link" data-bs-toggle="modal" data-bs-target="#follower_modal"><b>{self.jane.follower_count()}</b> Followers</button>', html)

    def test_user_profile_has_chat_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a valign="left" class="btn" href="/user_profile/{self.jane.id}/create_chat/" style="padding-top: 10px; padding-bottom: 10px; color:white; background-color: brown; text-transform:uppercase; font-size: 14px">\n                                <i class="bi bi-messenger" style="font-size: 0.9rem"></i>\n                                Chat\n                              </a>', html)

    def test_user_profile_has_invite_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a id="Invite" class="btn" data-bs-toggle="modal" data-bs-target="#exampleModal_1" style="padding-top: 10px; padding-bottom: 10px; color:white; background-color: brown; text-transform:uppercase; font-size: 14px">\n                              <i class="bi bi-envelope" style="font-size: 0.9rem"></i>\n                              Invite\n                            </a>', html)

    def test_user_profile_has_follow_button_when_not_followed(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button class=\'btn btn-primary\' style="padding-top: 10px; padding-bottom: 10px; color:white; background-color: LIGHT-BLUE; text-transform:uppercase; font-size: 14px">\n                              Follow\n                            </button>', html)

    def test_user_profile_has_unfollow_button_when_followed(self):
        self.client.login(email=self.john.email, password='Password123')
        self.john.toggle_follow(self.jane)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button class=\'btn btn-secondary\' style="padding-top: 10px; padding-bottom: 10px; color:white; background-color: GREY; text-transform:uppercase; font-size: 14px">\n                              Unfollow\n                            </button>', html)

    def test_follow_button_in_user_profile_works(self):
        self.client.login(email=self.john.email, password='Password123')
        before_followee_count = self.john.followee_count()
        response = self.client.get('/follow_toggle/2/', follow=True)
        redirect_url = self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_followee_count = self.john.followee_count()
        self.assertNotEqual(before_followee_count, after_followee_count)

    def test_unfollow_button_in_user_profile_works(self):
        self.client.login(email=self.john.email, password='Password123')
        self.john.followees.add(self.jane)
        before_followee_count = self.john.followee_count()
        response = self.client.get('/unfollow/2/', follow=True)
        redirect_url = self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_followee_count = self.john.followee_count()
        self.assertNotEqual(before_followee_count, after_followee_count)
