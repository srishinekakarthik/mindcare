from django.contrib import admin
from .models import Institution, UserProfile, MoodEntry

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role', 'institution', 'created_at']
    list_filter = ['role', 'institution', 'created_at']
    search_fields = ['user__username', 'user__email', 'institution__name']
    ordering = ['-created_at']

@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'mood_value', 'mood_label', 'reason', 'created_at']
    list_filter = ['mood_value', 'mood_label', 'created_at']
    search_fields = ['user__username', 'user__email', 'reason', 'notes']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
