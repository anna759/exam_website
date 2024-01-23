import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from subprocess import run
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user ,timestamp):
        return six.text_type(user.pk) + six.text_type(timestamp)+six.text_type(user.email_verified)
    
generate_token =TokenGenerator()

