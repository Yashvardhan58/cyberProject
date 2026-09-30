"""
Celery Application Initialization for Adaptive UEBA Insider Threat Detection.
"""

import os
from celery import Celery

# Default settings module for Celery worker
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

app = Celery("config")

# Namespace 'CELERY' implies all celery configs must have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed Django apps
app.autodiscover_tasks()
