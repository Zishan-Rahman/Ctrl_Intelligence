from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.tests.helpers import reverse_with_next

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
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_book_profile_has_correct_details(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        html = response.content.decode('utf8')
        self.assertIn(f'<img src="{self.book.medium_url}" alt="a">', html)
        self.assertIn(f'<h3 class="book-title">{self.book.title}</h3>', html)
        self.assertIn(f'<p class="book-isbn">ISBN: {self.book.isbn}</p>', html)
        self.assertIn(f'<p class="book-author">Author: {self.book.author}</p>', html)
        self.assertIn(f'<p class="book-pub-year">Published Year: {str(self.book.pub_year)}</p>', html)
        self.assertIn(f'<p class="book-publisher">Publisher: {self.book.publisher}</p>', html)

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
