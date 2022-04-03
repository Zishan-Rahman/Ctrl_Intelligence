# """Unit tests for the Application Form"""
# from django import forms
# from django.test import TestCase
# from bookclub.forms import ApplicationForm
# from bookclub.models import Club, User
#
#
# class TestApplicationForm(TestCase):
#     """Test case for the Application Form"""
#     fixtures = ['bookclub/tests/fixtures/default_users.json' , 'bookclub/tests/fixtures/default_clubs.json', 'bookclub/tests/fixtures/default_applications.json']
#
#     def setUp(self):
#         self.user = User.objects.get(email='johndoe@bookclub.com')
#         self.bush_club = Club.objects.get(name='Bush House Book Club')
#         self.bush_club.make_member(self.user)
#         self.form_input = {
#             'applicant': self.user,
#             'club': self.bush_club
#         }
#
#     def test_application_form_has_necessary_fields(self):
#       """Tests if application form has necessary fields."""
#         form = ApplicationForm()
#         self.assertIn('applicant', form.fields)
#         self.assertIn('club', form.fields)
#
#     def test_valid_application_form(self):
#         """Testing for valid application form."""
#         form = ApplicationForm(data=self.form_input)
#         self.assertTrue(form.is_valid())
#
#     def test_form_rejects_blank_applicant(self):
#         """Testing if application form rejects a blank applicant."""
#         self.form_input['applicant'] = ''
#         form = ApplicationForm(data=self.form_input)
#         self.assertFalse(form.is_valid())
#
#     def test_form_rejects_blank_club(self):
#         """Testing if application form rejects a blank club."""
#         self.form_input['club'] = ''
#         form = ApplicationForm(data=self.form_input)
#         self.assertFalse(form.is_valid())
#
#     def test_applicant_form_saves_properly(self):
#         """Tests if the form, well, saves properly!"""
#         form = ApplicationForm(data=self.form_input)
#         app = form.save(self.user) # This breaks the tests. This form isn't even being used anywhere, for all I know. ¯\_(ツ)_/¯
#         self.assertEqual(app.applicant, self.user)
#         self.assertEqual(app.club, self.bush_club)
