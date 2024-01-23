from django.apps import AppConfig

from django.apps import AppConfig
class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

    def ready(self):
        import user.signals
        #from .scheduler import scheduler
        #scheduler.start()


