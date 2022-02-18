from django.urls import reverse


def nums(first_number, last_number, step=1):
    return range(first_number, last_number+1, step)

def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url

class LogInTester:
#check if user is logged in
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()
