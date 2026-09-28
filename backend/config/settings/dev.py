"""
Development Settings for Local Development.
"""

from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# CORS allow all for development ease
CORS_ALLOW_ALL_ORIGINS = True
