"""Tests of the application view."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Application
from bookclub.tests.helpers import reverse_with_next
from django.contrib import messages


class ApplicationViewTestCase(TestCase):
    """Tests of the application view."""

    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json', 'bookclub/tests/fixtures/default_applications.json']

    def setUp(self):
        self.url = reverse('applications')
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')
        self.user = User.objects.get(pk=1)

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

    def test_get_applications_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_application_list_with_pagination(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_applications(settings.APPLICATIONS_PER_PAGE*2+3-1)
        response = self.client.get(reverse('applications'))
        print(response.context['applicants'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications.html')
        self.assertEqual(len(response.context['applicants']), settings.APPLICATIONS_PER_PAGE)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('applications') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications.html')
        self.assertEqual(len(response.context['applicants']), settings.APPLICATIONS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('applications') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications.html')
        self.assertEqual(len(response.context['applicants']), settings.APPLICATIONS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('applications') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applications.html')
        self.assertEqual(len(response.context['applicants']), 2)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())


    def _create_test_applications(self,application_count=10):
        for id in range(1,application_count+1, 1):
            created_user = User.objects.create(
                email=f'user{id}@test.org',
                password='Password123',
                first_name=f'First{id}',
                last_name=f'Last{id}',
                public_bio=f'Bio {id}',
                favourite_genre=f'genre {id}',
                location=f'City {id}',
                age=18+id
            )
            created_club=Club.objects.create(
                owner_id=id,
                name=f'The {id} Book Club',
                location=f'City {id}',
                description=f'Description {id}',
                owner=created_user,
            )
            a=Application.objects.create(
                applicant=created_user,
                club=created_club,
            )
            print(a)
