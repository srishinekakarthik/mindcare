from django.contrib import admin
from .models import (
    Institution, UserProfile, MoodEntry,
    CounselorProfile, Availability, Session, SessionFeedback,
    AssessmentResult, Resource, PeerSupportPost, PeerSupportComment,
)


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role', 'institution', 'is_approved', 'created_at']
    list_filter = ['role', 'is_approved', 'institution', 'created_at']
    search_fields = ['user__username', 'user__email', 'institution__name']
    ordering = ['-created_at']
    actions = ['approve_counselors']

    @admin.action(description="Approve selected counselor accounts")
    def approve_counselors(self, request, queryset):
        updated = queryset.filter(role='counselor').update(is_approved=True)
        self.message_user(request, f"Approved {updated} counselor account(s).")


@admin.register(CounselorProfile)
class CounselorProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_profile', 'title', 'specialties']
    search_fields = ['user_profile__user__username', 'title', 'specialties']


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ['id', 'counselor', 'date', 'start_time', 'is_booked']
    list_filter = ['is_booked', 'date']
    ordering = ['date', 'start_time']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'counselor', 'date', 'start_time', 'session_type', 'status']
    list_filter = ['status', 'session_type', 'date']
    search_fields = ['student__username', 'counselor__user_profile__user__username']
    ordering = ['-date', '-start_time']


@admin.register(SessionFeedback)
class SessionFeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'counselor_user', 'rating', 'created_at']
    list_filter = ['rating']


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'mood_value', 'mood_label', 'reason', 'created_at']
    list_filter = ['mood_value', 'mood_label', 'created_at']
    search_fields = ['user__username', 'user__email', 'reason', 'notes']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'assessment_type', 'total_score', 'severity', 'created_at']
    list_filter = ['assessment_type', 'severity', 'created_at']
    search_fields = ['user__username']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'is_published', 'view_count', 'created_at']
    list_filter = ['category', 'is_published']
    search_fields = ['title', 'description']


@admin.register(PeerSupportPost)
class PeerSupportPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'is_anonymous', 'is_flagged', 'created_at']
    list_filter = ['is_anonymous', 'is_flagged']
    search_fields = ['title', 'body']


@admin.register(PeerSupportComment)
class PeerSupportCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'author', 'is_anonymous', 'created_at']
    list_filter = ['is_anonymous']
