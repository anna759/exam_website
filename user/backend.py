# backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.utils import timezone

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, otp=None, **kwargs):
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return None

        # Check if the user's password is valid
        if user.check_password(password):
            # Check OTP if user is a learner with a verified email
            if user.is_learner and user.email_verified:
                if user.otp_secret and user.otp_secret == otp and (timezone.now() - user.otp_created_at).seconds < 300:
                    #user.otp_secret
                    return user
                else:
                    return None
            elif user.is_lectuer:
                return user

        return None
