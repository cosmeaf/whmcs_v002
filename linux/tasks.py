from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import logging

# Configurar logger
logger = logging.getLogger(__name__)

@shared_task
def send_email_task(subject, to_email, template_name=None, context=None, body=None):
    """
    Envia um e-mail, com ou sem template, e trata possíveis erros.

    :param subject: Assunto do e-mail.
    :param to_email: Endereço de e-mail do destinatário.
    :param template_name: Nome do template HTML para o corpo do e-mail (opcional).
    :param context: Contexto para renderizar o template (opcional).
    :param body: Corpo do e-mail em texto simples (opcional).
    """
    try:
        if template_name and context:
            # Renderizar o corpo do e-mail a partir do template
            message = render_to_string(template_name, context)
            content_subtype = 'html'
        elif body:
            # Usar o corpo do e-mail em texto simples
            message = body
            content_subtype = 'plain'
        else:
            raise ValueError("Você deve fornecer um template ou um corpo de e-mail.")

        # Criar o e-mail
        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email]
        )
        
        # Definir o tipo de conteúdo
        email.content_subtype = content_subtype
        
        # Enviar o e-mail
        email.send()

    except ValueError as e:
        logger.error(f"Erro ao enviar e-mail: {e}")
        raise

    except Exception as e:
        logger.error(f"Erro inesperado ao enviar e-mail: {e}")
        raise
