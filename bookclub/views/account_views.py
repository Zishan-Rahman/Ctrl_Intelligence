"""Account related views."""
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from bookclub.templates import *
from bookclub.forms import PasswordForm, SignUpForm, UserForm, UserPostForm, LogInForm
from bookclub.models import Club, User, UserPost
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import MultipleObjectMixin
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    forms = {'login': LogInForm(),
            'signup': SignUpForm(),
            'password_reset': PasswordResetForm(),
            }
    return render(request, 'landing_page.html', {'form':forms})



def password_reset_request(request):
    site = get_current_site(request)
    if request.method == "POST":
        forms = {'login': LogInForm(),
            'signup': SignUpForm(),
            'password_reset': PasswordResetForm(request.POST),
            }
        password_reset_form = forms['password_reset']
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "main/password/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': site,
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'bookwise0000@gmail.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    messages.success(request,
                                     'A message with reset password instructions has been sent to your inbox. Please '
                                     'check your spam folder.')
                    return redirect("landing_page")
            messages.error(request, 'An invalid email has been entered.')
    forms = {'login': LogInForm(),
            'signup': SignUpForm(),
            'password_reset': PasswordResetForm(),
            }
    return render(request, 'landing_page.html', {'form': forms})


class PasswordView(LoginRequiredMixin, FormView):
    """View that handles password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('home')

    def post(self, request, *args, **kwargs):
        current_user = request.user
        form = self.form_class(user=current_user, data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return render(request, 'password.html', {"form": form})

    def get(self, request, *args, **kwargs):
        current_user = request.user
        form = self.form_class()
        return render(request, 'password.html', {"form": form})
