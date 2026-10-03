"""
Django Base Settings for Adaptive UEBA Insider Threat Detection System.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env if present
env_file = BASE_DIR / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-ueba-adaptive-threat-detection-key-2026-2027"
)

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "corsheaders",
    # Local Apps
    "apps.users",
    "apps.alerts",
    "apps.baselines",
    "apps.explanations",
    "apps.verdicts",
    "apps.metrics",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database Configuration: SQLite default for local lightweight dev, PostgreSQL for MacBook
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework Settings
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True

# -----------------------------------------------------------------------------
# Celery 5.3 + Redis 7 Asynchronous Task Configuration
# -----------------------------------------------------------------------------
# 1. Dual-Environment Broker Fallback:
#    - Inside Docker: Uses REDIS_URL=redis://redis:6379/0 (internal container network)
#    - Local Windows: Falls back to redis://localhost:6379/0 without throwing KeyError
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 2. Source of Truth & No Result Backend Bloat:
#    - Explanations and governance audit logs are persisted directly in PostgreSQL/SQLite.
#    - Redis is strictly used as a lightweight message broker, saving memory.
CELERY_TASK_IGNORE_RESULT = True

# 3. Message Redelivery & Reliability (acks_late):
#    - Worker acknowledges the task only AFTER execution finishes successfully.
#    - If a worker crashes mid-task, the job is not lost and is safely redelivered.
CELERY_TASK_ACKS_LATE = True

# 4. Free LLM API Protection (Prefetch Multiplier = 1):
#    - Prevents a worker from hogging multiple Claude jobs in advance.
#    - Each worker thread pulls only 1 task at a time, preventing token bursts and rate-limit spikes.
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# 5. Execution Time Limits (Guard against hanging LLM network calls):
#    - Soft Limit (60s): Raises SoftTimeLimitExceeded inside the task to gracefully mark row FAILED.
#    - Hard Limit (90s): Hard SIGKILL by OS if process hangs indefinitely.
CELERY_TASK_SOFT_TIME_LIMIT = 60
CELERY_TASK_TIME_LIMIT = 90

# 6. Broker Connection Retries & Visibility Timeout:
#    - Retries Redis connection on boot if Redis container starts slightly after the worker.
#    - visibility_timeout (3600s = 1hr): Ensures tasks are not prematurely redelivered while executing.
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600}

# 7. Queue Segregation (Fast Lane vs. Slow Lane):
#    - queue "llm": Consumed exclusively by worker-llm (concurrency 2) for Claude API calls.
#    - queue "governance": Consumed by worker-governance (concurrency 1) for CPU-bound pandas baseline audits.
#    - Prevents heavy periodic governance checks from blocking urgent SOC alert explanations.
CELERY_TASK_ROUTES = {
    "apps.explanations.tasks.generate_alert_explanation_task": {"queue": "llm"},
    "*.generate_alert_explanation_task": {"queue": "llm"},
    "apps.baselines.tasks.run_baseline_governance_task": {"queue": "governance"},
    "governance.*": {"queue": "governance"},
}
