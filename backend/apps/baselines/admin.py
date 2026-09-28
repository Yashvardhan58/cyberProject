from django.contrib import admin
from .models import UserBaseline, GovernanceLog

@admin.register(UserBaseline)
class UserBaselineAdmin(admin.ModelAdmin):
    list_display = ("user", "baseline_date", "is_suppressed", "suppression_reason")
    list_filter = ("is_suppressed", "baseline_date")
    search_fields = ("user__name", "user__employee_id")

@admin.register(GovernanceLog)
class GovernanceLogAdmin(admin.ModelAdmin):
    list_display = ("user", "check_date", "verdict", "suspicion_score", "reason")
    list_filter = ("verdict", "check_date")
    search_fields = ("user__name", "reason")
