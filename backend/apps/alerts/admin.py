from django.contrib import admin
from .models import RiskScore, Alert, SHAPValue

class SHAPValueInline(admin.TabularInline):
    model = SHAPValue
    extra = 0

@admin.register(RiskScore)
class RiskScoreAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "final_risk", "severity", "xgb_score", "if_score")
    list_filter = ("severity", "date")
    search_fields = ("user__name", "user__employee_id")

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "severity", "status", "title", "created_at")
    list_filter = ("severity", "status", "created_at")
    search_fields = ("user__name", "title", "description")
    inlines = [SHAPValueInline]

@admin.register(SHAPValue)
class SHAPValueAdmin(admin.ModelAdmin):
    list_display = ("alert", "rank", "feature_name", "shap_value", "actual_value", "direction")
    list_filter = ("direction", "rank")
