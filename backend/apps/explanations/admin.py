from django.contrib import admin
from .models import Explanation, ChatSession, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0

@admin.register(Explanation)
class ExplanationAdmin(admin.ModelAdmin):
    list_display = ("alert", "faithfulness_score", "model_name", "created_at")
    search_fields = ("alert__title", "explanation_text")

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("session_token", "alert", "analyst_name", "updated_at")
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "created_at")
    list_filter = ("role",)
