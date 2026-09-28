"""
URL Configuration for Adaptive UEBA Insider Threat Detection System.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/alerts/', include('apps.alerts.urls')),
    path('api/v1/verdicts/', include('apps.verdicts.urls')),
    path('api/v1/baselines/', include('apps.baselines.urls')),
    path('api/v1/metrics/', include('apps.metrics.urls')),
    path('api/v1/explanations/', include('apps.explanations.urls')),
]
