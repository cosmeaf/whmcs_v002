# support/models/smtp_model.py

from django.db import models
from django.core.mail import get_connection
from django.core.exceptions import ValidationError
from support.utils.email_services import EMAIL_SERVICES

class EmailSettings(models.Model):
    EMAIL_BACKEND_CHOICES = [
        ('django.core.mail.backends.smtp.EmailBackend', 'SMTP'),
        ('django.core.mail.backends.console.EmailBackend', 'Console'),
        ('django.core.mail.backends.filebased.EmailBackend', 'File-based'),
    ]

    email_backend = models.CharField(
        max_length=255, 
        choices=EMAIL_BACKEND_CHOICES, 
        default='django.core.mail.backends.smtp.EmailBackend'
    )
    email_service = models.CharField(
        max_length=255, 
        choices=[(service, service) for service in EMAIL_SERVICES.keys()] + [('Manual', 'Manual')], 
        blank=True, 
        null=True
    )
    email_host = models.CharField(max_length=255, blank=True, null=True)
    email_port = models.IntegerField(blank=True, null=True)
    email_use_tls = models.BooleanField(default=True)
    email_use_ssl = models.BooleanField(default=False)
    email_host_user = models.EmailField(blank=True, null=True)
    email_host_password = models.CharField(max_length=255, blank=True, null=True)
    default_from_email = models.EmailField()

    def __str__(self):
        return self.email_host_user if self.email_host_user else "Email Settings"

    def clean(self):
        if self.email_service and self.email_service != 'Manual':
            service_settings = EMAIL_SERVICES.get(self.email_service, {})
            self.email_host = service_settings.get('host', self.email_host)
            self.email_port = service_settings.get('port', self.email_port)
            self.email_use_tls = service_settings.get('use_tls', self.email_use_tls)
            self.email_use_ssl = service_settings.get('use_ssl', self.email_use_ssl)

        if self.email_backend == 'django.core.mail.backends.smtp.EmailBackend':
            if not self.email_host or not self.email_port:
                raise ValidationError("SMTP configuration requires both email_host and email_port.")
            if self.email_use_tls and self.email_use_ssl:
                raise ValidationError("Cannot use both TLS and SSL. Please choose one.")
            try:
                connection = get_connection(
                    backend=self.email_backend,
                    host=self.email_host,
                    port=self.email_port,
                    username=self.email_host_user,
                    password=self.email_host_password,
                    use_tls=self.email_use_tls,
                    use_ssl=self.email_use_ssl,
                )
                connection.open()
            except Exception as e:
                raise ValidationError(f"SMTP configuration is invalid: {e}")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
