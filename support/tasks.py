# support/tasks.py
from celery import shared_task
import pandas as pd
from django.contrib.auth import get_user_model
from celery.exceptions import MaxRetriesExceededError
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_user_creation(data):
    UserModel = get_user_model()
    generated_users = []

    logger.info(f"Iniciando a criação de usuários. Total de usuários no lote: {len(data)}")

    for user_data in data:
        nome_completo = user_data['nome_completo']
        email = user_data['email']
        username = user_data['username']
        password = user_data['password']
        first_name = user_data['first_name']
        last_name = user_data['last_name']

        try:
            # Verifica se o username OU email já existe
            if not UserModel.objects.filter(username=username).exists() and not UserModel.objects.filter(email=email).exists():
                # Cria o usuário se username e email não existirem
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
                logger.info(f"Usuário criado: {username} ({email})")
            else:
                logger.warning(f"Usuário {username} ou email {email} já existe. Pulando criação.")
        except Exception as e:
            logger.error(f"Erro ao criar usuário {username} ({email}): {str(e)}")
            continue  # Continua com o próximo usuário, mesmo se houver erro

    logger.info(f"Finalizando a criação de usuários. Total criado: {len(generated_users)}")

    return generated_users
