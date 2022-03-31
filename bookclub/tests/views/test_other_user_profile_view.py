from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import reverse_with_next

class OtherUserProfileTest(TestCase):

    fixtures = ['bookclub/tests/fixtures/default_users.json']

    def setUp(self):
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.url = reverse('user_profile', kwargs={'user_id': self.jane.id})

    def test_other_user_profile_url(self):
        self.assertEqual(self.url,f'/user_profile/{self.jane.id}/')

    def test_other_user_profile_uses_correct_template(self):
        login = self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile.html')

    def test_get_other_user_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_other_user_profile_has_correct_details(self):
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

    def test_view_profile_shows_following_number(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a style="text-decoration: none; color: #292b2c"><h4 class="text-left fw-bold link"><strong>{self.john.followee_count()}</strong></h4></a>', html)

    def test_view_profile_shows_followers_number(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<a style="text-decoration: none; color: #292b2c"><h4 class="text-left fw-bold link"><strong>{self.john.follower_count()}</strong></h4></a>', html)

    def test_view_profile_has_following_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button class="link" data-bs-toggle="modal" data-bs-target="#following_modal">Following</button>', html)

    def test_view_profile_has_followers_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'Followers</button>', html)

    def test_other_user_profile_has_message_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'style="padding: 15px; text-transform:uppercase; font-size: 14px"><i class="bi bi-chat-dots"></i> Message</a>', html)

    def test_other_user_profile_has_invite_button(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button id="bookwiseGeneralBtn" class="btn btn-lg" data-bs-toggle="modal" '
                      f'data-bs-target="#exampleModal_1" style="padding: 15px; text-transform:uppercase; font-size: '
                      f'14px"><i class="bi bi-envelope"></i> Invite</button>', html)

    def test_other_user_profile_has_follow_button_when_not_followed(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'Follow</button>', html)

    def test_other_user_profile_has_unfollow_button_when_following_user(self):
        self.client.login(email=self.john.email, password='Password123')
        self.john.toggle_follow(self.jane)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('Unfollow</button>', html)

    def test_follow_button_in_other_user_profile_works(self):
        self.client.login(email=self.john.email, password='Password123')
        before_followee_count = self.john.followee_count()
        response = self.client.get(f'/user_profile/{self.jane.id}/follow/', follow=True)
        redirect_url = self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_followee_count = self.john.followee_count()
        self.assertNotEqual(before_followee_count, after_followee_count)

    def test_unfollow_button_in_other_user_profile_works(self):
        self.client.login(email=self.john.email, password='Password123')
        self.john.followees.add(self.jane)
        before_followee_count = self.john.followee_count()
        response = self.client.get(f'/user_profile/{self.jane.id}/unfollow/', follow=True)
        redirect_url = self.url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_followee_count = self.john.followee_count()
        self.assertNotEqual(before_followee_count, after_followee_count)
