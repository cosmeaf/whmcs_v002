# support/tasks.py

from celery import shared_task
import pandas as pd
from django.contrib.auth import get_user_model

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
