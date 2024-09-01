# core/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Define as configurações padrão do Django para o celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Usa as configurações do settings.py do Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre e carrega automaticamente tasks de todos os apps registrados no Django
app.autodiscover_tasks()
