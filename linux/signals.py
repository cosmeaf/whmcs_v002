import os
import subprocess
from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from linux.utilities.create_user import create_linux_user
from linux.utilities.delete_user import delete_linux_user
from linux.utilities.update_user import update_password


@receiver(post_save, sender=User)
def create_user_signal(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        create_linux_user(instance.username, instance.password)

@receiver(post_delete, sender=User)
def delete_user_signal(sender, instance, **kwargs):
    delete_linux_user(instance.username)

@receiver(pre_save, sender=User)
def update_password_signal(sender, instance, **kwargs):
    if instance.pk:
        user = User.objects.get(pk=instance.pk)
        if user.password != instance.password:
            update_password(instance.username, instance.password)
