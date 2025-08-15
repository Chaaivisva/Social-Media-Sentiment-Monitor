from django.contrib import admin
from .models import SocialPost, TrackedKeyword

@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'sentiment_label', 'emotion_label', 'platform', 'timestamp')
    list_filter = ('sentiment_label', 'emotion_label', 'platform')
    search_fields = ('title', 'description')

@admin.register(TrackedKeyword)
class TrackedKeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'is_active', 'added_by')
    list_filter = ('is_active',)
    search_fields = ('keyword',)