from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# ──────────────────────────────────────────────────────────────────────────
# Core identity
# ──────────────────────────────────────────────────────────────────────────

class Institution(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    Roles:
      student   - belongs to an institution, uses platform for self-help/booking
      staff     - belongs to an institution, gets an institution-level oversight dashboard
      counselor - serves all institutions (no institution tie), must be approved by an admin
      admin     - superuser-level, serves all institutions, created only via Django admin/createsuperuser
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'University Staff'),
        ('counselor', 'Counselor'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Institution only applies to student/staff. Counselors & admins serve everyone.
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, null=True, blank=True
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    # Counselor accounts are not usable until an admin approves them.
    is_approved = models.BooleanField(default=True)

    supabase_user_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        inst = f" at {self.institution.name}" if self.institution else ""
        return f"{self.user.username} - {self.role}{inst}"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser

    @property
    def is_staff_role(self):
        return self.role == 'staff'

    @property
    def is_counselor(self):
        return self.role == 'counselor'

    @property
    def is_student(self):
        return self.role == 'student'


# ──────────────────────────────────────────────────────────────────────────
# Counseling: counselor profiles, availability, sessions
# ──────────────────────────────────────────────────────────────────────────

class CounselorProfile(models.Model):
    """Extra info for users with role='counselor'. Created on approval."""
    user_profile = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name='counselor_profile'
    )
    title = models.CharField(max_length=150, blank=True, help_text="e.g. Licensed Clinical Psychologist")
    specialties = models.CharField(max_length=300, blank=True, help_text="Comma-separated, e.g. Anxiety, Depression")
    bio = models.TextField(blank=True)
    session_length_minutes = models.PositiveIntegerField(default=50)

    def __str__(self):
        return f"Counselor: {self.user_profile.user.get_full_name() or self.user_profile.user.username}"

    @property
    def specialty_list(self):
        return [s.strip() for s in self.specialties.split(',') if s.strip()]

    @property
    def average_rating(self):
        agg = self.user_profile.user.received_feedback.aggregate(models.Avg('rating'))
        return round(agg['rating__avg'], 1) if agg['rating__avg'] else None


class Availability(models.Model):
    """A single open slot a counselor has made available for booking."""
    counselor = models.ForeignKey(
        CounselorProfile, on_delete=models.CASCADE, related_name='availability_slots'
    )
    date = models.DateField()
    start_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ('counselor', 'date', 'start_time')
        verbose_name_plural = 'Availability slots'

    def __str__(self):
        status = "booked" if self.is_booked else "open"
        return f"{self.counselor} - {self.date} {self.start_time} ({status})"


class Session(models.Model):
    """A booked counseling session (replaces the old localStorage-only booking flow)."""
    SESSION_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('group', 'Group'),
    ]
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booked_sessions')
    counselor = models.ForeignKey(
        CounselorProfile, on_delete=models.CASCADE, related_name='sessions'
    )
    availability = models.OneToOneField(
        Availability, on_delete=models.SET_NULL, null=True, blank=True, related_name='session'
    )
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='individual')
    date = models.DateField()
    start_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    student_notes = models.TextField(blank=True, help_text="Notes the student shared before the session")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.student.username} with {self.counselor} on {self.date} {self.start_time}"


class SessionFeedback(models.Model):
    """Optional rating left by a student after a completed session."""
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name='feedback')
    counselor_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_feedback'
    )
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.counselor_user.username} - {self.rating}★"


# ──────────────────────────────────────────────────────────────────────────
# Mood tracking (existing)
# ──────────────────────────────────────────────────────────────────────────

class MoodEntry(models.Model):
    MOOD_CHOICES = [
        (1, 'Very Unpleasant'),
        (2, 'Unpleasant'),
        (3, 'Slightly Unpleasant'),
        (4, 'Neutral'),
        (5, 'Slightly Pleasant'),
        (6, 'Pleasant'),
        (7, 'Very Pleasant'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_entries')
    mood_value = models.IntegerField(choices=MOOD_CHOICES)
    mood_label = models.CharField(max_length=50)
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mood Entry'
        verbose_name_plural = 'Mood Entries'

    def __str__(self):
        return f"{self.user.username} - {self.mood_label} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


# ──────────────────────────────────────────────────────────────────────────
# Self-assessment
# ──────────────────────────────────────────────────────────────────────────

class AssessmentResult(models.Model):
    """Stores a completed self-assessment (e.g. PHQ-9 / GAD-7 style) submission."""
    ASSESSMENT_TYPE_CHOICES = [
        ('phq9', 'Depression (PHQ-9 style)'),
        ('gad7', 'Anxiety (GAD-7 style)'),
        ('stress', 'Stress Check'),
    ]
    SEVERITY_CHOICES = [
        ('minimal', 'Minimal'),
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('moderately_severe', 'Moderately Severe'),
        ('severe', 'Severe'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_results')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES)
    answers = models.JSONField(default=list, help_text="List of integer answers per question")
    total_score = models.IntegerField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_assessment_type_display()} ({self.severity})"


# ──────────────────────────────────────────────────────────────────────────
# Resources
# ──────────────────────────────────────────────────────────────────────────

class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('exercise', 'Guided Exercise'),
        ('hotline', 'Crisis Hotline'),
        ('worksheet', 'Worksheet'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    url = models.URLField(blank=True, help_text="External link, if applicable")
    body = models.TextField(blank=True, help_text="Inline content, if hosted directly")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_resources'
    )
    view_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# ──────────────────────────────────────────────────────────────────────────
# Peer support (anonymous-by-default community board)
# ──────────────────────────────────────────────────────────────────────────

class PeerSupportPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='peer_posts')
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_anonymous = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False, help_text="Flagged for counselor/admin review")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def display_name(self):
        if self.is_anonymous:
            return "Anonymous"
        return self.author.get_full_name() or self.author.username


class PeerSupportComment(models.Model):
    post = models.ForeignKey(PeerSupportPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='peer_comments')
    body = models.TextField()
    is_anonymous = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment on '{self.post.title}'"

    @property
    def display_name(self):
        if self.is_anonymous:
            return "Anonymous"
        return self.author.get_full_name() or self.author.username
