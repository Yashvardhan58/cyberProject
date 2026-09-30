"""
Django config package initialization.
Exposes celery_app so tasks are loaded on Django startup.
"""

from .celery import app as celery_app

__all__ = ("celery_app",)
