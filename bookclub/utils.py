from lib2to3.pgen2.tokenize import generate_tokens
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.id) + six.text_type(timestamp) + six.text_type(user.is_email_verified))

    
generate_token = TokenGenerator()