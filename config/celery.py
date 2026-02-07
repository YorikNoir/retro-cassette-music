"""
Celery configuration for async task processing (song generation).
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('retro_cassette_music')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
