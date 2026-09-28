from django.contrib import admin
from .models import AnalystVerdict

@admin.register(AnalystVerdict)
class AnalystVerdictAdmin(admin.ModelAdmin):
    list_display = ("alert", "verdict", "analyst_name", "submitted_at")
    list_filter = ("verdict", "submitted_at")
    search_fields = ("alert__title", "analyst_name", "analyst_note")
