from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import connection
from django.db.models import Avg, Count, Q
from django.conf import settings
from django.utils import timezone
import json
import logging
import datetime

from .models import (
    Institution, UserProfile, MoodEntry,
    CounselorProfile, Availability, Session, SessionFeedback,
    AssessmentResult, Resource, PeerSupportPost, PeerSupportComment,
)
from .permissions import get_profile, role_required

logger = logging.getLogger(__name__)
try:
    from supabase_config import get_supabase_client, get_supabase_admin_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

try:
    from gemini_config import generate_mental_health_response, is_mental_health_related, get_off_topic_response, GEMINI_AVAILABLE
    GEMINI_AVAILABLE = GEMINI_AVAILABLE
except ImportError:
    GEMINI_AVAILABLE = False


# ──────────────────────────────────────────────────────────────────────────
# Basic page views
# ──────────────────────────────────────────────────────────────────────────

def home(request):
    return redirect('login')


def login_view(request):
    return render(request, 'login.html')


def signup_view(request):
    return render(request, 'signup.html')


def role_redirect_url(profile):
    """Where to send a user right after login/signup, based on their role."""
    if profile.is_admin:
        return '/dashboard/'
    if profile.role == 'staff':
        return '/dashboard/'
    if profile.role == 'counselor':
        return '/counselor/dashboard/'
    return '/mindcare-home/'


# ──────────────────────────────────────────────────────────────────────────
# Auth APIs
# ──────────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def signup_api(request):
    """
    Roles available at signup: student, staff, counselor.
    Admin accounts are never created through signup - only via
    `createsuperuser` / the Django admin panel, per platform policy.
    Counselor accounts are created with is_approved=False and cannot use
    counselor features until an admin approves them.
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        institution_name = data.get('institution', '').strip()
        role = data.get('role', 'student')

        if role not in ('student', 'staff', 'counselor'):
            return JsonResponse({'error': 'Invalid role selected'}, status=400)

        required_fields = [username, email, password]
        if role in ('student', 'staff'):
            required_fields.append(institution_name)

        if not all(required_fields):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Username already exists. Please choose a different username.'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'An account with this email already exists.'}, status=400)

        institution = None
        if role in ('student', 'staff'):
            institution, _ = Institution.objects.get_or_create(name=institution_name)

        django_user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Counselors get Django staff access for admin-panel visibility, but
        # this is NOT the same as platform "admin" role - admins are never
        # created here.
        if role == 'counselor':
            django_user.is_staff = True
            django_user.save()

        profile = UserProfile.objects.create(
            user=django_user,
            institution=institution,
            role=role,
            is_approved=(role != 'counselor'),  # counselors need admin approval
        )

        if role == 'counselor':
            CounselorProfile.objects.create(user_profile=profile)
            return JsonResponse({
                'success': True,
                'pending_approval': True,
                'message': 'Your counselor account has been created and is pending admin approval. You will be able to log in once approved.',
            })

        from django.contrib.auth import authenticate, login as django_login
        user_auth = authenticate(username=username, password=password)
        if user_auth:
            django_login(request, user_auth)

        return JsonResponse({
            'success': True,
            'message': 'Account created successfully',
            'user': {
                'email': email,
                'username': username,
                'role': role,
                'institution': profile.institution.name if profile.institution else None,
            },
            'redirect_url': role_redirect_url(profile)
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return JsonResponse({'error': 'Email and password required'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        user_auth = authenticate(username=user.username, password=password)
        if not user_auth:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

        try:
            profile = UserProfile.objects.get(user=user_auth)
        except UserProfile.DoesNotExist:
            if user_auth.is_superuser:
                # Automatically create a profile for superusers created via CLI
                profile = UserProfile.objects.create(
                    user=user_auth,
                    role='admin',
                    is_approved=True
                )
            else:
                return JsonResponse({'error': 'User profile not found'}, status=404)

        if profile.role == 'counselor' and not profile.is_approved and not user_auth.is_superuser:
            return JsonResponse({
                'error': 'Your counselor account is still pending admin approval.'
            }, status=403)

        django_login(request, user_auth)
        return JsonResponse({
            'success': True,
            'message': 'Login successful',
            'user': {
                'email': user_auth.email,
                'username': user_auth.username,
                'role': 'admin' if profile.is_admin else profile.role,
                'institution': profile.institution.name if profile.institution else None,
            },
            'redirect_url': role_redirect_url(profile)
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def logout_api(request):
    django_logout(request)
    return JsonResponse({'success': True, 'message': 'Logged out successfully'})


@require_http_methods(["GET"])
def current_user_api(request):
    """Used by templates/JS to get the authoritative server-side identity
    instead of trusting localStorage."""
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False})

    profile = get_profile(request.user)
    if not profile:
        return JsonResponse({'authenticated': False})

    return JsonResponse({
        'authenticated': True,
        'username': request.user.username,
        'email': request.user.email,
        'role': 'admin' if profile.is_admin else profile.role,
        'institution': profile.institution.name if profile.institution else None,
        'is_approved': profile.is_approved,
    })


# ──────────────────────────────────────────────────────────────────────────
# Student-facing pages (real data, not hardcoded)
# ──────────────────────────────────────────────────────────────────────────

@login_required
def mindcare_home(request):
    profile = get_profile(request.user)
    if not profile:
        messages.error(request, 'User profile not found')
        return redirect('login')

    # Staff/admin land on their dashboards instead of the student home.
    if profile.is_admin or profile.role == 'staff':
        return redirect('analytics_dashboard')
    if profile.role == 'counselor':
        return redirect('counselor_dashboard')

    hour = timezone.localtime().hour
    if hour < 12:
        time_of_day = 'morning'
    elif hour < 18:
        time_of_day = 'afternoon'
    else:
        time_of_day = 'evening'

    upcoming_sessions = Session.objects.filter(
        student=request.user, status='confirmed', date__gte=timezone.localdate()
    ).select_related('counselor__user_profile__user')[:3]

    recent_moods = MoodEntry.objects.filter(user=request.user)[:7]

    context = {
        'time_of_day': time_of_day,
        'profile': profile,
        'upcoming_sessions': upcoming_sessions,
        'recent_moods': recent_moods,
    }
    return render(request, 'mindcare_home.html', context)


@login_required
def ai_support(request):
    return render(request, 'ai_support.html')


@login_required
def self_assessment(request):
    profile = get_profile(request.user)
    past_results = AssessmentResult.objects.filter(user=request.user)[:5]
    context = {'past_results': past_results}
    return render(request, 'self_assessment.html', context)


@login_required
def mood_tracker(request):
    return render(request, 'mood_tracker.html')


@login_required
def peer_support(request):
    posts = PeerSupportPost.objects.filter(is_flagged=False).select_related('author').prefetch_related('comments')[:50]
    context = {'posts': posts}
    return render(request, 'peer_support.html', context)


@login_required
@require_http_methods(["POST"])
def peer_support_comment(request, post_id):
    post = get_object_or_404(PeerSupportPost, id=post_id)
    try:
        data = json.loads(request.body)
        body = data.get('body', '').strip()
        is_anonymous = bool(data.get('is_anonymous', True))
        if not body:
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)

        comment = PeerSupportComment.objects.create(
            post=post, author=request.user, body=body, is_anonymous=is_anonymous
        )
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'body': comment.body,
                'display_name': comment.display_name,
                'created_at': comment.created_at.isoformat(),
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)


@login_required
@require_http_methods(["POST"])
def create_peer_post_api(request):
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        body = data.get('body', '').strip()
        is_anonymous = bool(data.get('is_anonymous', True))

        if not title or not body:
            return JsonResponse({'success': False, 'error': 'Title and body are required'}, status=400)

        post = PeerSupportPost.objects.create(
            author=request.user, title=title, body=body, is_anonymous=is_anonymous
        )
        return JsonResponse({
            'success': True,
            'post': {
                'id': post.id,
                'title': post.title,
                'body': post.body,
                'display_name': post.display_name,
                'created_at': post.created_at.isoformat(),
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)


@login_required
def resources(request):
    category = request.GET.get('category')
    qs = Resource.objects.filter(is_published=True)
    if category:
        qs = qs.filter(category=category)
    context = {
        'resources': qs,
        'categories': Resource.CATEGORY_CHOICES,
        'selected_category': category,
    }
    return render(request, 'resources.html', context)


@login_required
def resource_detail(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id, is_published=True)
    Resource.objects.filter(id=resource_id).update(view_count=resource.view_count + 1)
    return render(request, 'resources.html', {'resources': [resource], 'detail_view': True})


@login_required
@require_http_methods(["POST"])
def submit_assessment_api(request):
    """PHQ-9/GAD-7-style scoring: sum of answers (each 0-3) mapped to a severity band."""
    try:
        data = json.loads(request.body)
        assessment_type = data.get('assessment_type')
        answers = data.get('answers', [])

        if assessment_type not in dict(AssessmentResult.ASSESSMENT_TYPE_CHOICES):
            return JsonResponse({'success': False, 'error': 'Invalid assessment type'}, status=400)
        if not isinstance(answers, list) or not answers or not all(isinstance(a, int) and 0 <= a <= 3 for a in answers):
            return JsonResponse({'success': False, 'error': 'Answers must be a list of integers 0-3'}, status=400)

        total_score = sum(answers)
        max_score = len(answers) * 3
        ratio = total_score / max_score if max_score else 0

        if ratio < 0.2:
            severity = 'minimal'
        elif ratio < 0.4:
            severity = 'mild'
        elif ratio < 0.6:
            severity = 'moderate'
        elif ratio < 0.8:
            severity = 'moderately_severe'
        else:
            severity = 'severe'

        result = AssessmentResult.objects.create(
            user=request.user,
            assessment_type=assessment_type,
            answers=answers,
            total_score=total_score,
            severity=severity,
        )

        return JsonResponse({
            'success': True,
            'result': {
                'id': result.id,
                'total_score': result.total_score,
                'severity': result.severity,
                'severity_display': result.get_severity_display(),
                'created_at': result.created_at.isoformat(),
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)


# ──────────────────────────────────────────────────────────────────────────
# Booking system (student books real counselors / real availability)
# ──────────────────────────────────────────────────────────────────────────

@login_required
def book_session(request):
    profile = get_profile(request.user)
    if profile and profile.role not in ('student', 'staff') and not profile.is_admin:
        messages.error(request, 'Only students and staff can book counseling sessions.')
        return redirect('mindcare_home')

    counselors = CounselorProfile.objects.filter(
        user_profile__is_approved=True
    ).select_related('user_profile__user').annotate(
        upcoming_slot_count=Count(
            'availability_slots',
            filter=Q(availability_slots__is_booked=False, availability_slots__date__gte=timezone.localdate())
        )
    )

    upcoming_bookings = Session.objects.filter(
        student=request.user, status='confirmed', date__gte=timezone.localdate()
    ).select_related('counselor__user_profile__user')

    context = {
        'counselors': counselors,
        'upcoming_bookings': upcoming_bookings,
    }
    return render(request, 'book_session.html', context)


@login_required
@require_http_methods(["GET"])
def counselor_slots_api(request, counselor_id):
    """Open slots for a given counselor, for the next 14 days, grouped by date."""
    counselor = get_object_or_404(CounselorProfile, id=counselor_id, user_profile__is_approved=True)
    today = timezone.localdate()
    horizon = today + datetime.timedelta(days=14)

    slots = Availability.objects.filter(
        counselor=counselor, is_booked=False, date__gte=today, date__lte=horizon
    ).order_by('date', 'start_time')

    by_date = {}
    for slot in slots:
        by_date.setdefault(slot.date.isoformat(), []).append({
            'id': slot.id,
            'time': slot.start_time.strftime('%I:%M %p').lstrip('0'),
            'time_24': slot.start_time.strftime('%H:%M'),
        })

    return JsonResponse({
        'success': True,
        'counselor': {
            'id': counselor.id,
            'name': counselor.user_profile.user.get_full_name() or counselor.user_profile.user.username,
            'title': counselor.title,
            'specialties': counselor.specialty_list,
            'session_length_minutes': counselor.session_length_minutes,
        },
        'slots_by_date': by_date,
    })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_booking_api(request):
    profile = get_profile(request.user)
    if profile and profile.role not in ('student', 'staff') and not profile.is_admin:
        return JsonResponse({'success': False, 'error': 'Only students and staff can book sessions.'}, status=403)

    try:
        data = json.loads(request.body)
        slot_id = data.get('slot_id')
        session_type = data.get('session_type', 'individual')
        notes = data.get('notes', '')

        if session_type not in dict(Session.SESSION_TYPE_CHOICES):
            return JsonResponse({'success': False, 'error': 'Invalid session type'}, status=400)

        try:
            slot = Availability.objects.select_related('counselor__user_profile__user').get(id=slot_id, is_booked=False)
        except Availability.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'That slot is no longer available. Please pick another.'}, status=409)

        # Re-check at write time to avoid a race between two students booking the same slot.
        updated = Availability.objects.filter(id=slot.id, is_booked=False).update(is_booked=True)
        if not updated:
            return JsonResponse({'success': False, 'error': 'That slot was just booked by someone else.'}, status=409)

        session_obj = Session.objects.create(
            student=request.user,
            counselor=slot.counselor,
            availability=slot,
            session_type=session_type,
            date=slot.date,
            start_time=slot.start_time,
            student_notes=notes,
        )

        counselor_name = slot.counselor.user_profile.user.get_full_name() or slot.counselor.user_profile.user.username

        return JsonResponse({
            'success': True,
            'message': f"Your {session_obj.get_session_type_display()} session has been booked.",
            'booking': {
                'id': session_obj.id,
                'counselor': counselor_name,
                'date': session_obj.date.isoformat(),
                'time': session_obj.start_time.strftime('%I:%M %p').lstrip('0'),
                'type': session_obj.get_session_type_display(),
                'status': session_obj.status,
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def cancel_session_api(request, session_id):
    session_obj = get_object_or_404(Session, id=session_id, student=request.user)
    if session_obj.status != 'confirmed':
        return JsonResponse({'success': False, 'error': 'This session can no longer be cancelled.'}, status=400)

    session_obj.status = 'cancelled'
    session_obj.save(update_fields=['status', 'updated_at'])

    if session_obj.availability:
        session_obj.availability.is_booked = False
        session_obj.availability.save(update_fields=['is_booked'])

    return JsonResponse({'success': True, 'message': 'Session cancelled.'})


# ──────────────────────────────────────────────────────────────────────────
# Counselor-facing views
# ──────────────────────────────────────────────────────────────────────────

@role_required('counselor', require_approved=True)
def counselor_dashboard(request):
    profile = get_profile(request.user)
    counselor = get_object_or_404(CounselorProfile, user_profile=profile)

    today = timezone.localdate()
    upcoming_sessions = Session.objects.filter(
        counselor=counselor, status='confirmed', date__gte=today
    ).select_related('student').order_by('date', 'start_time')[:20]

    past_sessions = Session.objects.filter(
        counselor=counselor, status='completed'
    ).select_related('student').order_by('-date', '-start_time')[:10]

    open_slot_count = Availability.objects.filter(counselor=counselor, is_booked=False, date__gte=today).count()

    context = {
        'counselor': counselor,
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
        'open_slot_count': open_slot_count,
        'average_rating': counselor.average_rating,
    }
    return render(request, 'counselor_dashboard.html', context)


@role_required('counselor', require_approved=True)
def counselor_availability(request):
    profile = get_profile(request.user)
    counselor = get_object_or_404(CounselorProfile, user_profile=profile)
    today = timezone.localdate()

    slots = Availability.objects.filter(
        counselor=counselor, date__gte=today
    ).order_by('date', 'start_time')

    context = {'counselor': counselor, 'slots': slots}
    return render(request, 'counselor_availability.html', context)


@role_required('counselor', require_approved=True)
@csrf_exempt
@require_http_methods(["POST"])
def add_availability_api(request):
    profile = get_profile(request.user)
    counselor = get_object_or_404(CounselorProfile, user_profile=profile)

    try:
        data = json.loads(request.body)
        date_str = data.get('date')
        time_str = data.get('time')  # "HH:MM" 24h

        slot_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        slot_time = datetime.datetime.strptime(time_str, '%H:%M').time()

        if slot_date < timezone.localdate():
            return JsonResponse({'success': False, 'error': 'Cannot add availability in the past.'}, status=400)

        slot, created = Availability.objects.get_or_create(
            counselor=counselor, date=slot_date, start_time=slot_time
        )
        if not created:
            return JsonResponse({'success': False, 'error': 'That slot already exists.'}, status=400)

        return JsonResponse({
            'success': True,
            'slot': {
                'id': slot.id,
                'date': slot.date.isoformat(),
                'time': slot.start_time.strftime('%I:%M %p').lstrip('0'),
            }
        })
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Invalid date or time format.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)


@role_required('counselor', require_approved=True)
@csrf_exempt
@require_http_methods(["POST"])
def delete_availability_api(request, slot_id):
    profile = get_profile(request.user)
    counselor = get_object_or_404(CounselorProfile, user_profile=profile)
    slot = get_object_or_404(Availability, id=slot_id, counselor=counselor)

    if slot.is_booked:
        return JsonResponse({'success': False, 'error': 'Cannot delete a slot that has been booked. Cancel the session first.'}, status=400)

    slot.delete()
    return JsonResponse({'success': True})


@role_required('counselor', require_approved=True)
@csrf_exempt
@require_http_methods(["POST"])
def complete_session_api(request, session_id):
    profile = get_profile(request.user)
    counselor = get_object_or_404(CounselorProfile, user_profile=profile)
    session_obj = get_object_or_404(Session, id=session_id, counselor=counselor)

    session_obj.status = 'completed'
    session_obj.save(update_fields=['status', 'updated_at'])
    return JsonResponse({'success': True})


@role_required('counselor', require_approved=True)
def counselor_resources(request):
    resources = Resource.objects.filter(created_by=request.user).order_by('-created_at')
    context = {
        'resources': resources,
        'categories': Resource.CATEGORY_CHOICES,
    }
    return render(request, 'counselor_resources.html', context)


@role_required('counselor', require_approved=True)
@csrf_exempt
@require_http_methods(["POST"])
def add_resource_api(request):
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        category = data.get('category')
        url = data.get('url', '').strip()

        if not title or not category:
            return JsonResponse({'success': False, 'error': 'Title and category are required.'}, status=400)

        valid_categories = dict(Resource.CATEGORY_CHOICES).keys()
        if category not in valid_categories:
            return JsonResponse({'success': False, 'error': 'Invalid category.'}, status=400)

        resource = Resource.objects.create(
            title=title,
            description=description,
            category=category,
            url=url,
            created_by=request.user,
            is_published=True
        )

        return JsonResponse({
            'success': True,
            'resource': {
                'id': resource.id,
                'title': resource.title,
                'category_display': resource.get_category_display(),
                'created_at': resource.created_at.isoformat(),
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# ──────────────────────────────────────────────────────────────────────────
# Admin / Staff analytics (computed from real data, scoped by role)
# ──────────────────────────────────────────────────────────────────────────

def _build_analytics(scope_qs_users, scope_sessions, scope_moods, days=30):
    """Shared analytics builder. scope_qs_users/scope_sessions/scope_moods are
    pre-filtered querysets (platform-wide for admins, institution-only for staff)."""
    since = timezone.localdate() - datetime.timedelta(days=days)

    active_users = scope_qs_users.filter(
        Q(last_login__date__gte=since)
    ).count()

    total_bookings = scope_sessions.filter(created_at__date__gte=since).count()
    completed_sessions = scope_sessions.filter(status='completed').count()
    cancelled_sessions = scope_sessions.filter(status='cancelled').count()

    # "Crisis alerts" = severe assessment results in scope, recent window.
    crisis_alerts = AssessmentResult.objects.filter(
        user__in=scope_qs_users, severity__in=['severe', 'moderately_severe'],
        created_at__date__gte=since
    ).count()

    mood_dist_qs = scope_moods.filter(created_at__date__gte=since).values('mood_value').annotate(count=Count('id'))
    mood_buckets = {'Excellent': 0, 'Good': 0, 'Neutral': 0, 'Low': 0, 'Very Low': 0}
    bucket_map = {7: 'Excellent', 6: 'Excellent', 5: 'Good', 4: 'Neutral', 3: 'Low', 2: 'Very Low', 1: 'Very Low'}
    for row in mood_dist_qs:
        bucket = bucket_map.get(row['mood_value'])
        if bucket:
            mood_buckets[bucket] += row['count']

    # Engagement over last 7 days: mood entries logged per day (proxy for usage).
    engagement_labels = []
    engagement_counts = []
    booking_counts = []
    for i in range(6, -1, -1):
        day = timezone.localdate() - datetime.timedelta(days=i)
        engagement_labels.append(day.strftime('%a'))
        engagement_counts.append(scope_moods.filter(created_at__date=day).count())
        booking_counts.append(scope_sessions.filter(created_at__date=day).count())

    recent_sessions = scope_sessions.select_related(
        'student', 'counselor__user_profile__user'
    ).order_by('-created_at')[:6]

    return {
        'active_users': active_users,
        'total_bookings': total_bookings,
        'completed_sessions': completed_sessions,
        'cancelled_sessions': cancelled_sessions,
        'crisis_alerts': crisis_alerts,
        'mood_buckets': mood_buckets,
        'mood_bucket_labels_json': json.dumps(list(mood_buckets.keys())),
        'mood_bucket_values_json': json.dumps(list(mood_buckets.values())),
        'engagement_labels': engagement_labels,
        'engagement_labels_json': json.dumps(engagement_labels),
        'engagement_counts': engagement_counts,
        'engagement_counts_json': json.dumps(engagement_counts),
        'booking_counts': booking_counts,
        'booking_counts_json': json.dumps(booking_counts),
        'recent_sessions': recent_sessions,
        'window_days': days,
    }


@login_required
def analytics_dashboard(request):
    """Admins see platform-wide analytics. Staff see institution-only, anonymized
    aggregates for their own institution. Students/counselors are denied."""
    profile = get_profile(request.user)
    if not profile:
        messages.error(request, 'User profile not found')
        return redirect('login')

    if not (profile.is_admin or profile.role == 'staff'):
        messages.error(request, 'Access denied. Admin or staff privileges required.')
        return redirect('mindcare_home')

    if profile.is_admin:
        scope_users = User.objects.all()
        scope_sessions = Session.objects.all()
        scope_moods = MoodEntry.objects.all()
        scope_label = 'Platform-wide'
    else:
        # Staff: scoped strictly to their own institution, and only ever in
        # aggregate (no individual student identities are exposed here).
        institution_user_ids = UserProfile.objects.filter(
            institution=profile.institution, role='student'
        ).values_list('user_id', flat=True)
        scope_users = User.objects.filter(id__in=institution_user_ids)
        scope_sessions = Session.objects.filter(student_id__in=institution_user_ids)
        scope_moods = MoodEntry.objects.filter(user_id__in=institution_user_ids)
        scope_label = profile.institution.name if profile.institution else 'Your institution'

    analytics = _build_analytics(scope_users, scope_sessions, scope_moods)
    context = {
        'is_admin': profile.is_admin,
        'scope_label': scope_label,
        **analytics,
    }
    return render(request, 'analytics_dashboard.html', context)


@role_required('admin')
def database_viewer(request):
    profile = get_profile(request.user)

    is_system_admin = profile.is_admin
    if is_system_admin:
        visible_profiles = UserProfile.objects.all().select_related('user', 'institution').order_by('-created_at')
        visible_users = User.objects.all()
        visible_moods = MoodEntry.objects.all()
        visible_institutions = Institution.objects.all()
    else:
        visible_profiles = UserProfile.objects.filter(
            institution=profile.institution, role='student'
        ).order_by('-created_at')
        visible_users = User.objects.filter(userprofile__in=visible_profiles)
        visible_moods = MoodEntry.objects.filter(user__in=visible_users)
        visible_institutions = Institution.objects.filter(id=profile.institution_id)

    context = {
        'users': visible_users,
        'profiles': visible_profiles,
        'institutions': visible_institutions,
        'mood_entries': visible_moods[:20],
        'total_users': visible_profiles.count(),
        'total_profiles': visible_profiles.count(),
        'total_institutions': visible_institutions.count(),
        'total_mood_entries': visible_moods.count(),
        'total_admin': User.objects.filter(is_superuser=True).count() if is_system_admin else 0,
    }
    return render(request, 'database_viewer.html', context)


@role_required('admin')
def manage_counselors(request):
    pending = CounselorProfile.objects.filter(
        user_profile__is_approved=False
    ).select_related('user_profile__user')
    approved = CounselorProfile.objects.filter(
        user_profile__is_approved=True
    ).select_related('user_profile__user')

    context = {'pending_counselors': pending, 'approved_counselors': approved}
    return render(request, 'manage_counselors.html', context)


@role_required('admin')
@csrf_exempt
@require_http_methods(["POST"])
def approve_counselor_api(request, profile_id):
    counselor = get_object_or_404(CounselorProfile, id=profile_id)
    counselor.user_profile.is_approved = True
    counselor.user_profile.save(update_fields=['is_approved'])
    return JsonResponse({'success': True})


@role_required('admin')
@csrf_exempt
@require_http_methods(["POST"])
def reject_counselor_api(request, profile_id):
    counselor = get_object_or_404(CounselorProfile, id=profile_id)
    user = counselor.user_profile.user
    user.delete()  # cascades to UserProfile -> CounselorProfile
    return JsonResponse({'success': True})


# ──────────────────────────────────────────────────────────────────────────
# Mood tracking APIs
# ──────────────────────────────────────────────────────────────────────────

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def save_mood_api(request):
    """Save mood data to database"""
    try:
        data = json.loads(request.body)

        mood_value = data.get('mood', {}).get('value')
        mood_label = data.get('mood', {}).get('label')
        reasons = data.get('reasons', [])
        custom_reason = data.get('customReason', '')
        timestamp = data.get('timestamp')

        if not mood_value or not mood_label:
            return JsonResponse({
                'success': False,
                'error': 'Mood value and label are required'
            }, status=400)

        reason_text = ''
        if reasons:
            reason_text += ', '.join(reasons)
        if custom_reason:
            if reason_text:
                reason_text += f' | Custom: {custom_reason}'
            else:
                reason_text = f'Custom: {custom_reason}'

        mood_entry = MoodEntry.objects.create(
            user=request.user,
            mood_value=mood_value,
            mood_label=mood_label,
            reason=reason_text,
            notes=f"Timestamp: {timestamp}" if timestamp else None
        )

        return JsonResponse({
            'success': True,
            'message': 'Mood saved successfully',
            'mood_id': mood_entry.id,
            'created_at': mood_entry.created_at.isoformat()
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_mood_history_api(request):
    """Get mood history for the current user"""
    try:
        mood_entries = MoodEntry.objects.filter(user=request.user).order_by('-created_at')

        mood_history = []
        for entry in mood_entries:
            mood_history.append({
                'id': entry.id,
                'mood_value': entry.mood_value,
                'mood_label': entry.mood_label,
                'reason': entry.reason,
                'notes': entry.notes,
                'created_at': entry.created_at.isoformat(),
                'updated_at': entry.updated_at.isoformat()
            })

        return JsonResponse({
            'success': True,
            'mood_history': mood_history,
            'total_entries': len(mood_history)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ──────────────────────────────────────────────────────────────────────────
# AI chat (Gemini)
# ──────────────────────────────────────────────────────────────────────────

@login_required
@require_http_methods(["POST"])
def gemini_chat_api(request):
    """Handle AI chat requests using Gemini API"""
    try:
        try:
            from gemini_config import generate_mental_health_response
        except ImportError:
            from gemini_fallback import generate_mental_health_response

        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_history = data.get('conversation_history', [])

        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            }, status=400)

        gemini_response = generate_mental_health_response(user_message, conversation_history)

        if gemini_response.get('error'):
            return JsonResponse({
                'success': False,
                'error': gemini_response['error'],
                'fallback_response': "I'm here to listen and support you. Could you tell me more about what's on your mind?"
            }, status=500)

        return JsonResponse({
            'success': True,
            'response': gemini_response['text'],
            'safety_flags': gemini_response.get('safety_flags', []),
            'model': gemini_response.get('model', 'gemini-1.5-flash'),
            'timestamp': gemini_response.get('timestamp', ''),
            'crisis_detected': 'crisis_detected' in gemini_response.get('safety_flags', [])
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'fallback_response': "I'm experiencing technical difficulties. Please contact campus counseling for immediate support."
        }, status=500)


# ──────────────────────────────────────────────────────────────────────────
# Health checks / env debug (operational, unchanged behavior)
# ──────────────────────────────────────────────────────────────────────────

def healthz(request):
    """Health check endpoint - no auth required"""
    env_ok = bool(settings.SUPABASE_URL and settings.GEMINI_API_KEY)

    db_ok = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            db_ok = True
    except Exception:
        db_ok = False

    return JsonResponse({
        'env_ok': env_ok,
        'db_ok': db_ok
    }, status=200)


def env_debug(request):
    """Environment debug endpoint - only available in DEBUG mode"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Not available in production'}, status=403)

    return JsonResponse({
        'has_supabase_url': bool(settings.SUPABASE_URL),
        'has_supabase_anon': bool(settings.SUPABASE_ANON_KEY),
        'has_gemini': bool(settings.GEMINI_API_KEY),
        'has_database_url': bool(settings.DATABASES['default'].get('NAME') != 'db.sqlite3')
    }, status=200)


def test_env_vars(request):
    """Test endpoint to check environment variables on Render"""
    import os

    is_production = bool(os.getenv("RENDER") or os.getenv("DYNO") or os.getenv("RAILWAY_ENVIRONMENT"))

    env_status = {
        'environment': 'PRODUCTION' if is_production else 'LOCAL DEVELOPMENT',
        'render_detected': bool(os.getenv("RENDER")),
        'heroku_detected': bool(os.getenv("DYNO")),
        'railway_detected': bool(os.getenv("RAILWAY_ENVIRONMENT")),
        'env_vars': {
            'DJANGO_SECRET_KEY': 'SET' if os.getenv('DJANGO_SECRET_KEY') else 'NOT SET',
            'SECRET_KEY': 'SET' if os.getenv('SECRET_KEY') else 'NOT SET',
            'DEBUG': os.getenv('DEBUG', 'NOT SET'),
            'ALLOWED_HOSTS': os.getenv('ALLOWED_HOSTS', 'NOT SET'),
            'DATABASE_URL': 'SET' if os.getenv('DATABASE_URL') else 'NOT SET',
            'SUPABASE_URL': 'SET' if os.getenv('SUPABASE_URL') else 'NOT SET',
            'SUPABASE_ANON_KEY': 'SET' if os.getenv('SUPABASE_ANON_KEY') else 'NOT SET',
            'GEMINI_API_KEY': 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET',
        },
        'django_settings': {
            'SECRET_KEY': 'SET' if settings.SECRET_KEY else 'NOT SET',
            'DEBUG': settings.DEBUG,
            'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
            'DATABASE_ENGINE': settings.DATABASES['default']['ENGINE'],
            'SUPABASE_URL': 'SET' if settings.SUPABASE_URL else 'NOT SET',
            'GEMINI_API_KEY': 'SET' if settings.GEMINI_API_KEY else 'NOT SET',
        }
    }

    return JsonResponse(env_status, status=200)


def debug_env_vars(request):
    """Debug endpoint to check environment variables in detail"""
    import os

    debug_info = {
        'environment': 'PRODUCTION' if os.getenv("RENDER") else 'LOCAL',
        'render_detected': bool(os.getenv("RENDER")),
        'raw_env_vars': {
            'GEMINI_API_KEY': 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET',
            'SUPABASE_URL': 'SET' if os.getenv('SUPABASE_URL') else 'NOT SET',
            'DATABASE_URL': 'SET' if os.getenv('DATABASE_URL') else 'NOT SET',
        },
        'django_settings': {
            'GEMINI_API_KEY': 'SET' if settings.GEMINI_API_KEY else 'NOT SET',
            'SUPABASE_URL': 'SET' if settings.SUPABASE_URL else 'NOT SET',
        },
        'gemini_config_status': {
            'GEMINI_AVAILABLE': GEMINI_AVAILABLE,
            'import_success': True
        }
    }

    try:
        from gemini_config import GEMINI_AVAILABLE as GEMINI_AVAILABLE_IMPORT
        debug_info['gemini_config_status']['GEMINI_AVAILABLE_IMPORT'] = GEMINI_AVAILABLE_IMPORT
    except Exception as e:
        debug_info['gemini_config_status']['import_error'] = str(e)

    return JsonResponse(debug_info, status=200)


def simple_env_test(request):
    """Very simple environment test - just show raw env vars"""
    import os

    relevant_vars = {}
    for key, value in os.environ.items():
        if any(key.startswith(prefix) for prefix in ['GEMINI', 'SUPABASE', 'DATABASE', 'DEBUG', 'ALLOWED']):
            if 'KEY' in key or 'URL' in key:
                masked = value[:10] + "..." + value[-4:] if len(value) > 14 else "***"
                relevant_vars[key] = masked
            else:
                relevant_vars[key] = value

    return JsonResponse({
        'message': 'Simple environment test',
        'render_detected': bool(os.getenv('RENDER')),
        'environment_variables': relevant_vars,
        'gemini_key_exists': bool(os.getenv('GEMINI_API_KEY')),
        'gemini_key_length': len(os.getenv('GEMINI_API_KEY', '')),
    }, status=200)


def manual_env_setup(request):
    """Manual environment setup for testing - DEBUG only"""
    if not settings.DEBUG:
        return JsonResponse({'error': 'Not available in production'}, status=403)
    return JsonResponse({
        'message': 'This endpoint is a no-op placeholder; set GEMINI_API_KEY in your real environment instead.',
    }, status=200)
