"""Tests of the individual applications view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Application
from django.contrib import messages

class MyApplicationViewTestCase(TestCase):
    
    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json', 'bookclub/tests/fixtures/default_applications.json']
    
    def setUp(self):
        self.url = reverse('my_applications')
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')
        self.sam = User.objects.get(email='samdoe@bookclub.com')

        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.somerset_club = Club.objects.get(name='Somerset House Book Club')
        self.strand_club = Club.objects.get(name='Strand House Book Club')
        
    def test_my_application_url(self):
        self.assertEqual(self.url,'/my_applications/')
    
    def test_application_has_correct_details(self):
        self.client.login(email=self.joe.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertNotIn('You have no pending applications.', html)
        self.assertIn('<td>Bush House Book Club</td>', html)
        self.assertIn('<td>Bush House Official Book Club!</td>', html)
        self.assertIn('<td>Strand, London</td>', html)
        self.assertIn('<td>Strand House Book Club</td>', html)
        self.assertIn('<td>Strand House Official Book Club!</td>', html)
        self.assertIn('<td>Strand, London</td>', html)
        self.assertIn('<td>Somerset House Book Club</td>', html)
        self.assertIn('<td>Somerset House Official Book Club!</td>', html)
        self.assertIn('<td>Strand, London</td>', html)
        self.client.logout()
        
    def test_no_applications(self):
        self.client.login(email=self.jane.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn('You have no pending applications.', html)
        self.assertNotIn('<td>', html)
        self.assertNotIn('</td>', html)
        self.client.logout()
        