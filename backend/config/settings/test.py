"""
Test Settings for Pytest and Unit Testing.
Enables Celery eager mode for isolated execution without Redis.
"""

import os

# Guarantee REDIS_URL exists so base.py does not raise KeyError
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-mocked")

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "test-secret-key-for-pytest-execution"

# Eager execution for tests ONLY (tasks run in-process without worker or Redis)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# In-memory SQLite for fast, isolated test runs
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Fast password hasher for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
