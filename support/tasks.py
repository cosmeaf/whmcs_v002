# support/tasks.py
from celery import shared_task
import pandas as pd
from django.contrib.auth import get_user_model
from celery.exceptions import MaxRetriesExceededError
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
from support.models.smtp_model import EmailSettings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_email_task(self, subject, to, template_name=None, context=None):
    try:
        email_settings = EmailSettings.objects.first()
        if not email_settings:
            raise ValidationError("Email settings are not configured.")
        
        if template_name and context:
            html_content = render_to_string(f'emails/{template_name}', context)
            text_content = strip_tags(html_content)
        else:
            html_content = "This is a test email to validate the email server settings."
            text_content = html_content

        connection = get_connection(
            backend=email_settings.email_backend,
            host=email_settings.email_host,
            port=email_settings.email_port,
            username=email_settings.email_host_user,
            password=email_settings.email_host_password,
            use_tls=email_settings.email_use_tls,
            use_ssl=email_settings.email_use_ssl,
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=email_settings.default_from_email,
            to=[to],
            connection=connection
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    except ValidationError as e:
        logger.error(f"Validation error when sending email: {e}")
        raise self.retry(exc=e, countdown=10, max_retries=3)
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        try:
            raise self.retry(exc=e, countdown=10, max_retries=3)
        except MaxRetriesExceededError:
            logger.critical(f"Max retries exceeded for email to {to}.")
            # Aqui você pode adicionar código para salvar o erro em um modelo de log de erros
            # ou notificar o administrador do sistema.

@shared_task
def process_user_creation(data):
    UserModel = get_user_model()
    generated_users = []

    for user_data in data:
        nome_completo = user_data['nome_completo']
        email = user_data['email']
        username = user_data['username']
        password = user_data['password']
        first_name = user_data['first_name']
        last_name = user_data['last_name']

        if not UserModel.objects.filter(username=username).exists():
            user = UserModel.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            generated_users.append({
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'password': password
            })

    return generated_users
