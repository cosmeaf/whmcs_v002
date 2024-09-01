from django.db import models
from django.contrib.auth.models import User

class ProjectAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=255)
    access_time = models.DateTimeField(auto_now_add=True)
