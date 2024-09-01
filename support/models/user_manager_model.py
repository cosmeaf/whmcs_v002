from django.db import models

class UserManager(models.Model):
    class Meta:
        verbose_name = "User Manager"
        verbose_name_plural = "User Managers"

    def __str__(self):
        return "User Manager"
