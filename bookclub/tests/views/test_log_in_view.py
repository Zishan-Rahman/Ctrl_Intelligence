"""Tests of the log in view """
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import LogInForm
from bookclub.models import User, Club, ClubMembership
from bookclub.tests.helpers import LogInTester, reverse_with_next

class LogInViewTestCase(TestCase, LogInTester):
    """Tests of the log in view """

    def setUp(self):
        self.url = reverse('log_in')
        self.club1 = Club(name = 'Cobra Kai')
        self.club1.save()
        self.user1 = User.objects.create_user(
            email = 'sensei@cobrakai.dojo',
            name = 'Jonny Lawrence',
            personal_statement = 'I\'m gonna kick some ass',
            chess_experience = 'B',
            password = 'NoM1yag1Do!',
            bio = 'STRIKE FIRST - STRIKE HARD - NO MERCY',
        )

    def test_log_in_url(self):
        self.assertEqual(self.url, '/log_in/')

    def test_log_in_uses_correct_template(self):
        response = self.client.get(reverse('log_in'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_get_log_in(self):
        response = self.client.get(self.url)#getting login view
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)#display data entered again
        self.assertFalse(next)#line asserts that the template is rendered without value for next
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_get_log_in_with_redirect(self):
        destination_url = reverse('home')
        self.url = reverse_with_next('log_in', destination_url)
        response = self.client.get(self.url)#getting login view
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)#display data entered again
        self.assertEqual(next, destination_url)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_unsuccessful_log_in(self):
        form_input = {'email': 'sensei@cobrakai.dojo', 'password': 'WrongPassword123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)#display data entered again
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    #Test for unsuccessful log in: blank email
    def test_log_in_with_blank_username(self):
        form_input = { 'email': '', 'password': 'NoM1yag1Do' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_password(self):
        form_input = {'email': 'sensei@cobrakai.dojo', 'password': ''}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)#display data entered again
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_successful_log_in(self):
        form_input = {'email': 'sensei@cobrakai.dojo', 'password': 'NoM1yag1Do!'}#valid credential
        response = self.client.post(self.url, form_input, follow = True)#as we want client to follow redirect all the way to follow
        self.assertTrue(self._is_logged_in())
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_successful_log_in_with_redirect(self):
        redirect_url = reverse('home')
        form_input = {'email': 'sensei@cobrakai.dojo', 'password': 'NoM1yag1Do!', 'next': redirect_url }#valid credential
        response = self.client.post(self.url, form_input, follow = True)#as we want client to follow redirect all the way to follow
        self.assertTrue(self._is_logged_in())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_post_log_in_redirects_when_logged_in(self):
        self.client.login(email = self.user1.email, password = "NoM1yag1Do!")
        form_input = {'email': 'wronguser@example.org', 'password': 'WrongPassword123'}#valid credential
        response = self.client.post(self.url, form_input, follow=True)
        redirect_url = reverse('home')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_post_log_in_with_incorrect_credentials_and_redirect(self):
        redirect_url = reverse('home')
        form_input = { 'email': 'sensei@cobrakai.dojo', 'password': 'WrongPassword123', 'next': redirect_url }
        response = self.client.post(self.url, form_input)
        next = response.context['next']
        self.assertEqual(next, redirect_url)

    def test_valid_log_in_by_inactive_user(self):
        self.user1.is_active = False
        self.user1.save()
        form_input = {'email': 'sensei@cobrakai.dojo', 'password': 'NoM1yag1Do!'}#valid credential
        response = self.client.post(self.url, form_input, follow = True)#as we want client to follow redirect all the way to follow
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)#display data entered again
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
