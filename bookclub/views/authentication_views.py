"""Authenticated related views."""
from mimetypes import init
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse
from bookclub.forms import LogInForm, SignUpForm, PasswordForm
from bookclub.models import User
from .mixins import LoginProhibitedMixin
from django.contrib.auth.decorators import login_required
from bookclub.helpers import login_prohibited
from bookclub.views import club_views
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, force_text
from ..utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
import threading

#adapted from https://www.youtube.com/watch?v=Rbkc-0rqSw8

class email_sender(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class LogInView(LoginProhibitedMixin, View):
    """View that handles log in."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = 'home'

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            if not user.is_email_verified:
                messages.add_message(request, messages.ERROR, "Email is not verified, please check your inbox")
                return redirect("login")
            form = login(request, user)
            club_views.club_util(request)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'login.html', {'form': form, 'next': self.next})


def log_out(request):
    logout(request)
    return redirect('landing_page')

#adapted from https://www.youtube.com/watch?v=Rbkc-0rqSw8

def send_verification_email(user, request):
    site = get_current_site(request)
    subject = 'Bookwise: Activate your account'
    body = render_to_string('activate.html',{
        'user': user,
        'domain': site,
        'user_id': urlsafe_base64_encode(force_bytes(user.id)),
        'token': generate_token.make_token(user)
    })

    email = EmailMessage(subject=subject, body=body, from_email=settings.EMAIL_HOST_USER, to=[user.email])
    email_sender(email).start()


def activate(request, uid, token):
    try:
        id = force_text(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=id)
    except Exception as e:
        user = None
    
    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()

        messages.add_message(request, messages.SUCCESS, "Email verified")
        return redirect(reverse('login'))

    
    return render(request, "reverify_email.html")

#End of adapated code


@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(user, request)
            messages.add_message(request, messages.SUCCESS, 'Verification email sent')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})



