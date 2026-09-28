from django.contrib import admin
from .models import PeerGroup, UserProfile

@admin.register(PeerGroup)
class PeerGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "department", "role", "created_at")
    search_fields = ("department", "role")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "name", "role", "department", "current_risk_score", "current_severity")
    list_filter = ("current_severity", "department", "role")
    search_fields = ("employee_id", "name", "email")
    ordering = ("-current_risk_score",)
