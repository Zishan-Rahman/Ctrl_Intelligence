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
        html = response.content.decode('utf8')
        self.assertIn('<td>Somserset House Book Club</td>',  html)
        self.assertIn('<td>Joe</td>',  html)
        self.assertIn('<td>Doe</td>',  html)
        self.assertIn('<td>30</td>', html)
        self.assertIn('<td>Just another fake user again</td>',  html)
        self.assertIn('<td>Romance</td>',  html)
        self.assertIn('<td>Manchester</td>',  html)
        self.assertIn('<a class="btn btn-default"',  html)
      
    def test_no_applications(self):
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(reverse('applications'))
        html = response.content.decode('utf8')
        self.assertIn('You have no pending applications.', html)
        self.assertNotIn('<td>', html)
        self.assertNotIn('</td>', html)

    def test_multiple_applications_to_same_club(self):
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(reverse('applications'))
        html = response.content.decode('utf8')
        self.assertIn('<td>Somserset House Book Club</td>',  html)
        self.assertIn('<td>Joe</td>',  html)
        self.assertIn('<td>Doe</td>',  html)
        self.assertIn('<td>30</td>',  html)
        self.assertIn('<td>Just another fake user again</td>',  html)
        self.assertIn('<td>Romance</td>',  html)
        self.assertIn('<td>Manchester</td>',  html)
        self.assertIn('<a class="btn btn-default"',  html)

        self.assertIn('<td>Somserset House Book Club</td>',  html)
        self.assertIn('<td>John</td>',  html)
        self.assertIn('<td>Doe</td>',  html)
        self.assertIn('<td>39</td>',  html)
        self.assertIn("<td>I&#x27;m just an abstract concept!</td>",  html) #Apostrophe converted to &#x27;m in html source code
        self.assertIn('<td>Science fiction</td>',  html)
        self.assertIn('<td>London</td>',  html)
        self.assertIn('<a class="btn btn-default"',  html)

    def test_multiple_applications_to_different_clubs(self):
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(reverse('applications'))
        html = response.content.decode('utf8')
        self.assertIn('<td>Bush House Book Club</td>',  html)
        self.assertIn('<td>Joe</td>',  html)
        self.assertIn('<td>Doe</td>',  html)
        self.assertIn('<td>30</td>',  html)
        self.assertIn('<td>Just another fake user again</td>',  html)
        self.assertIn('<td>Romance</td>',  html)
        self.assertIn('<td>Manchester</td>',  html)
        self.assertIn('<a class="btn btn-default"',  html)

        self.assertIn('<td>Strand House Book Club</td>',  html)
        self.assertIn('<td>Joe</td>',  html)
        self.assertIn('<td>Doe</td>',  html)
        self.assertIn('<td>30</td>',  html)
        self.assertIn('<td>Just another fake user again</td>',  html)
        self.assertIn('<td>Romance</td>',  html)
        self.assertIn('<td>Manchester</td>',  html)
        self.assertIn('<a class="btn btn-default"',  html)

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
