from django.db.models.signals import post_save
from user.models import Usercutsom

from django.dispatch import receiver
from .models import profile

@receiver(post_save, sender=Usercutsom)
def create_profile(sender, instance, created,**kwargs):
    if created:
        profile.objects.create(user=instance)

@receiver(post_save, sender=Usercutsom)
def save_profile(sender, instance, created,**kwargs):
    instance.profile.save()