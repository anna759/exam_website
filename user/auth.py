from django.contrib.auth.backends import ModelBackend
from .models import Usercutsom

class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Usercutsom.objects.get(username=username)
        except Usercutsom.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None