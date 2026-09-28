from django.contrib import admin
from .models import ExperimentResult

@admin.register(ExperimentResult)
class ExperimentResultAdmin(admin.ModelAdmin):
    list_display = ("experiment_name", "title", "run_at")
    search_fields = ("experiment_name", "title", "summary")
