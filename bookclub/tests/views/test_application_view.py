"""Tests of the application view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Application
from django.contrib import messages


class ApplicationViewTestCase(TestCase):
    """Tests of the application view."""

    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json', 'bookclub/tests/fixtures/default_applications.json']

    def setUp(self):
        self.url = reverse('applications')
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')

        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.somerset_club = Club.objects.get(name='Somserset House Book Club')
        self.strand_club = Club.objects.get(name='Strand House Book Club')

        #self.somerset_app = Application.

    def test_application_url(self):
        self.assertEqual(self.url,'/applications/')

    def test_application_uses_correct_template(self):
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(reverse('applications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications.html')
    
    def test_application_has_correct_details(self):
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(reverse('applications'))
        self.assertInHTML('<td>Somserset House Book Club</td>',  self.response)
        self.assertInHTML('<td>Joe</td>',  self.response)
        self.assertInHTML('<td>Doe</td>',  self.response)
        self.assertInHTML('<td>30</td>', self. response)
        self.assertInHTML('<td>Just another fake user again</td>',  self.response)
        self.assertInHTML('<td>Romance</td>',  self.response)
        self.assertInHTML('<td>Manchester</td>',  self.response)
        self.assertInHTML('<a class="btn btn-default"',  self.response, count=2)
      
    def test_no_applications(self):
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(reverse('applications'))
        self.assertContains( response, 'You have no pending applications.')
        self.assertNotContains( response, '<td>')
        self.assertNotContains( response, '</td>')

    def test_multiple_applications_to_same_club(self):
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(reverse('applications'))
        self.assertInHTML('<td>Somserset House Book Club</td>',  response)
        self.assertInHTML('<td>Joe</td>',  response)
        self.assertInHTML('<td>Doe</td>',  response)
        self.assertInHTML('<td>30</td>',  response)
        self.assertInHTML('<td>Just another fake user again</td>',  response)
        self.assertInHTML('<td>Romance</td>',  response)
        self.assertInHTML('<td>Manchester</td>',  response)
        self.assertInHTML('<a class="btn btn-default"',  response, count=2)

        self.assertInHTML('<td>Somserset House Book Club</td>',  response)
        self.assertInHTML('<td>John</td>',  response)
        self.assertInHTML('<td>Doe</td>',  response)
        self.assertInHTML('<td>39</td>',  response)
        self.assertInHTML("<td>I'm just an abstract concept!</td>",  response)
        self.assertInHTML('<td>Science Fiction</td>',  response)
        self.assertInHTML('<td>London</td>',  response)
        self.assertInHTML('<a class="btn btn-default"',  response, count=2)

    def test_multiple_applications_to_different_clubs(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('applications'))
        self.assertInHTML('<td>Bush House Book Club</td>',  response)
        self.assertInHTML('<td>Joe</td>',  response)
        self.assertInHTML('<td>Doe</td>',  response)
        self.assertInHTML('<td>30</td>',  response)
        self.assertInHTML('<td>Just another fake user again</td>',  response)
        self.assertInHTML('<td>Romance</td>',  response)
        self.assertInHTML('<td>Manchester</td>',  response)
        self.assertInHTML('<a class="btn btn-default"',  response, count=2)

        self.assertInHTML('<td>Strand House Book Club</td>',  response)
        self.assertInHTML('<td>Joe</td>',  response)
        self.assertInHTML('<td>Doe</td>',  response)
        self.assertInHTML('<td>30</td>',  response)
        self.assertInHTML('<td>Just another fake user again</td>',  response)
        self.assertInHTML('<td>Romance</td>',  response)
        self.assertInHTML('<td>Manchester</td>',  response)
        self.assertInHTML('<a class="btn btn-default"',  response, count=2)

    def test_successful_accept(self):
        self.client.login(email=self.john.email, password='Password123')
        beforeCount = self.strand_club.get_number_of_members()
        response = self.client.get('/applications/accept/3/', follow=True)    
        redirect_url = reverse('applications')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        afterCount = self.strand_club.get_number_of_members()
        self.assertEqual(beforeCount, afterCount-1)

    def test_successful_reject(self):
        self.client.login(email=self.john.email, password='Password123')
        beforeCount = self.strand_club.get_number_of_members()
        response = self.client.get('/applications/remove/3/', follow=True)
        redirect_url = reverse('applications')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        afterCount = self.strand_club.get_number_of_members()
        self.assertEqual(beforeCount, afterCount) 
