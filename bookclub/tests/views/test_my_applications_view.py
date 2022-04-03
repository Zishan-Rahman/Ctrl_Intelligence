"""Unit tests of the Individual Applications View."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Application
from django.contrib import messages


class MyApplicationViewTestCase(TestCase):
    """Test case for the My Application View"""
    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json',
                'bookclub/tests/fixtures/default_applications.json']

    def setUp(self):
        self.url = reverse('my_applications')
        self.john = User.objects.get(email='johndoe@bookclub.com')
        self.jane = User.objects.get(email='janedoe@bookclub.com')
        self.joe = User.objects.get(email='joedoe@bookclub.com')
        self.sam = User.objects.get(email='samdoe@bookclub.com')

        self.bush_club = Club.objects.get(name='Bush House Book Club')
        self.somerset_club = Club.objects.get(name='Somerset House Book Club')
        self.strand_club = Club.objects.get(name='Strand House Book Club')

    def get_response_and_html(self):
        """Testing to get the response and html."""
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        return response, html

    def test_my_application_url(self):
        """Testing the my applications url."""
        self.assertEqual(self.url, '/my_applications/')

    def test_my_application_uses_correct_template(self):
        """Testing if my application uses correct template."""
        self.client.login(email=self.john.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_applications.html')

    def test_single_application_has_correct_details(self):
        """Testing if single application has the correct details."""
        self.client.login(email=self.john.email, password="Password123")
        response, html = self.get_response_and_html()
        self.assertNotIn('You have not made any applications yet.', html)
        self.assertIn('<td>Somerset House Book Club</td>', html)
        self.assertIn('<td>Somerset House Official Book Club!</td>', html)
        self.assertIn('<td>Strand, London</td>', html)

    def test_multiple_applications_have_correct_details(self):
        """Testing if multiple application have the correct details."""
        self.client.login(email=self.joe.email, password='Password123')
        response, html = self.get_response_and_html()
        self.assertNotIn('You have not made any applications yet.', html)
        self.assertIn('<td>Bush House Book Club</td>', html)
        self.assertIn('<td>Bush House Official Book Club!</td>', html)
        self.assertIn('<td>Strand, London</td>', html)
        self.assertIn('<td>Strand House Book Club</td>', html)
        self.assertIn('<td>Strand House Official Book Club!</td>', html)
        self.assertIn('<td>Strand, London</td>', html)
        self.assertIn('<td>Somerset House Book Club</td>', html)
        self.assertIn('<td>Somerset House Official Book Club!</td>', html)
        self.assertIn('<td>Strand, London</td>', html)

    def test_no_applications(self):
        """Testing if user has not made an application."""
        self.client.login(email=self.jane.email, password='Password123')
        response, html = self.get_response_and_html()
        self.assertIn('You have not made any applications yet.', html)
        self.assertNotIn('<td>', html)
        self.assertNotIn('</td>', html)

    def test_view_after_application_creation(self):
        """Testing for view after user created an application."""
        self.client.login(email=self.sam.email, password="Password123")
        self.application = Application.objects.create(applicant=self.sam, club=self.bush_club)
        response, html = self.get_response_and_html()
        self.assertNotIn('You have no pending applications.', html)
        self.assertIn('<td>Bush House Book Club</td>', html)
        self.assertIn('<td>Bush House Official Book Club!</td>', html)
        self.assertIn('<td>Strand, London</td>', html)

    def test_get_application_list_with_pagination(self):
        """Testing for application list with pagination."""
        self.client.login(email=self.john.email, password='Password123')
        self._create_test_my_applications(settings.APPLICATIONS_PER_PAGE * 2 + 3 - 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_applications.html')
        self.assertEqual(len(response.context['page_obj']), settings.APPLICATIONS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('my_applications') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_applications.html')
        self.assertEqual(len(response.context['page_obj']), settings.APPLICATIONS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('my_applications') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_applications.html')
        self.assertEqual(len(response.context['page_obj']), settings.APPLICATIONS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('my_applications') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_applications.html')
        self.assertEqual(len(response.context['page_obj']), 3)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())

    def _create_test_my_applications(self, my_applications_count=10):
        """Creation of applications."""
        my_apps = []
        for id in range(1, my_applications_count + 1, 1):
            created_club = Club.objects.create(
                owner_id=id,
                name=f'The {id} Book Club',
                location=f'City {id}',
                description=f'Description {id}',
                owner=User.objects.create(
                    email=f'user{id}@test.org',
                    password='Password123',
                    first_name=f'First{id}',
                    last_name=f'Last{id}',
                    public_bio=f'Bio {id}',
                    favourite_genre=f'genre {id}',
                    location=f'City {id}',
                    age=18 + id
                ),
            )
            my_apps.append(Application.objects.create(
                applicant=self.john,
                club=created_club,
            ))
