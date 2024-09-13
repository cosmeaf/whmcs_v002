import os
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


def get_file_path(instance, filename):
    """
    Gera um caminho único para salvar as imagens do perfil.
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('profile_pictures', filename)


class OtpCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp_code')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        expiration_time = self.created_at + timedelta(minutes=15)
        return timezone.now() <= expiration_time

class ProjectAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=255)
    access_time = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField('Imagem Perfil', upload_to=get_file_path, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(max_length=200, blank=True)
    github = models.URLField(max_length=200, blank=True)
    linkedin = models.URLField(max_length=200, blank=True)
    twitter = models.URLField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)

    def delete_old_image(self):
        """
        Remove a imagem antiga se for atualizada por uma nova.
        """
        if self.pk:  # Verifica se o objeto já existe no banco de dados
            try:
                old_profile = UserProfile.objects.get(pk=self.pk)
                if old_profile.image and old_profile.image != self.image and os.path.isfile(old_profile.image.path):
                    os.remove(old_profile.image.path)
            except UserProfile.DoesNotExist:
                pass

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para garantir que a imagem antiga seja deletada antes de salvar a nova.
        """
        self.delete_old_image()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Cliente / Usuário"
        verbose_name_plural = "Clientes / Usuários"
        indexes = [
            models.Index(fields=['user']),  # Índice no campo 'user'
        ]
