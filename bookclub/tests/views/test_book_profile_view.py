from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.tests.helpers import reverse_with_next
from django.contrib import messages

class BookProfileTest(TestCase):

    fixtures = ['bookclub/tests/fixtures/default_users.json','bookclub/tests/fixtures/default_books.json']

    def setUp(self):
        self.user = User.objects.get(email='johndoe@bookclub.com')
        self.book = Book.objects.get(isbn=12345678910)
        self.url = reverse('book_profile', kwargs={'book_id': self.book.id})

    def test_book_profile_url(self):
        self.assertEqual(self.url,f'/book_profile/{self.book.id}/')

    def test_book_profile_uses_correct_template(self):
        login = self.client.login(email='johndoe@bookclub.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_profile.html')

    def test_get_book_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('login', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_book_profile_has_correct_details(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'{self.book.large_url}', html)
        self.assertIn(f'{self.book.title}', html)
        self.assertIn(f'{self.book.isbn}', html)
        self.assertIn(f'{self.book.author}', html)
        self.assertIn(f'{str(self.book.pub_year)}', html)
        self.assertIn(f'{self.book.publisher}', html)

    def test_book_profile_has_favourite_button_when_book_is_not_in_favourites(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn" style="background-color: brown; color: white; font-size: '
                      f'24px"><i class="bi bi-star"></i></button>', html)

    def test_book_profile_has_unfavourite_button_when_book_is_in_favourites(self):
        self.client.login(email=self.user.email, password='Password123')
        self.user.favourite_books.add(self.book)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn" style="background-color: brown; color: white; font-size: '
                      f'24px"><i class="bi bi-star-fill"></i></button>', html)

    def test_favourite_button_in_book_profile_works(self):
        self.client.login(email=self.user.email, password='Password123')
        before_reading_list_count = self.user.favourite_books.count()
        response = self.client.get('/book_profile/1/favourite', follow=True)
        redirect_url = '/book_profile/1/'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        after_reading_list_count = self.user.favourite_books.count()
        self.assertNotEqual(before_reading_list_count, after_reading_list_count)

    def test_unfavourite_button_in_book_profile_works(self):
        self.client.login(email=self.user.email, password='Password123')
        self.user.favourite_books.add(self.book)
        before_reading_list_count = self.user.favourite_books.count()
        response = self.client.get('/book_profile/1/unfavourite', follow=True)
        redirect_url = '/book_profile/1/'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_reading_list_count = self.user.favourite_books.count()
        self.assertNotEqual(before_reading_list_count, after_reading_list_count)

    def test_book_profile_has_dropdown_to_rate_book(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'select class="form-select" name="ratings" id="ratings">', html)

    def test_book_profile_view_has_disqus_comments_section(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        assertString = """ <div id="disqus_thread"></div>
    <script>
        var disqus_config = function () {
        this.page.url = window.location.href;  // Replace PAGE_URL with your page's canonical URL variable
        this.page.identifier = window.location.href; // Replace PAGE_IDENTIFIER with your page's unique identifier variable
        };

        (function() { // DON'T EDIT BELOW THIS LINE
        var d = document, s = d.createElement('script');
        s.src = 'https://localhost-8000-b6e1mwjp94.disqus.com/embed.js';
        s.setAttribute('data-timestamp', +new Date());
        (d.head || d.body).appendChild(s);
        })();
    </script>
    <noscript>Please enable JavaScript to view the <a href="https://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
</div>
<script id="dsq-count-scr" src="//localhost-8000-b6e1mwjp94.disqus.com/count.js" async></script>"""
        self.assertIn(assertString,html)

    def test_book_profile_view_has_remove_from_reading_list_button_when_book_is_in_reading_list(self):
        self.client.login(email=self.user.email, password='Password123')
        self.user.currently_reading_books.add(self.book)
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn" style="background-color: brown; color: white; font-size: '
                      f'24px"><i class="bi bi-bookmarks-fill"></i></button>', html)

    def test_book_profile_view_has_add_to_reading_list_button_when_book_is_not_in_reading_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<button type="submit" class="btn" style="background-color: brown; color: white; font-size: '
                      f'24px"><i class="bi bi-bookmarks"></i></button>', html)

    def test_add_to_reading_list_in_book_profile_works(self):
        self.client.login(email=self.user.email, password='Password123')
        before_reading_list_count = self.user.currently_reading_books.count()
        response = self.client.get('/book_profile/1/add_to_reading_list/', follow=True)
        redirect_url = '/book_profile/1/'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        after_reading_list_count = self.user.currently_reading_books.count()
        self.assertNotEqual(before_reading_list_count, after_reading_list_count)

    def test_remove_from_reading_list_in_book_profile_works(self):
        self.client.login(email=self.user.email, password='Password123')
        self.user.currently_reading_books.add(self.book)
        before_reading_list_count = self.user.currently_reading_books.count()
        response = self.client.get('/book_profile/1/remove_from_reading_list/', follow=True)
        redirect_url = '/book_profile/1/'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        after_reading_list_count = self.user.currently_reading_books.count()
        self.assertNotEqual(before_reading_list_count, after_reading_list_count)

    # def test_book_profile_view_has_add_to_books_read_button(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #     response = self.client.get(self.url)
    #     html = response.content.decode('utf8')
    #     self.assertIn(f'<a class="btn btn-default" href="/add_to_books_read/1/" <span class="btn btn-dark" style=\'padding-top: 10px; padding-bottom: 10px; color:white; background-color: brown; text-transform:uppercase; font-size: 14px\'> Add to Books Read </span></a>', html)
