from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login as django_login, authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import connection
from django.conf import settings
import json
import logging
from .models import Institution, UserProfile

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

# Create your views here.
def home(request):
    return render(request, 'admin-student.html')

def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def mindcare_home(request):
    return render(request, 'mindcare_home.html')

def ai_support(request):
    return render(request, 'ai_support.html')

def book_session(request):
    return render(request, 'book_session.html')

def self_assessment(request):
    """Self assessment view"""
    return render(request, 'self_assessment.html')

def mood_tracker(request):
    """Mood tracker view"""
    return render(request, 'mood_tracker.html')

def peer_support(request):
    """Peer support view"""
    return render(request, 'peer_support.html')

def resources(request):
    """Resources view"""
    return render(request, 'resources.html')

@csrf_exempt
@require_http_methods(["POST"])
def save_mood_api(request):
    """Save mood data to database"""
    try:
        data = json.loads(request.body)
        
        # Extract mood data
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
        
        # Get user from request (if authenticated) or create anonymous entry
        user = None
        if request.user.is_authenticated:
            user = request.user
        else:
            # For anonymous users, try to get user from localStorage data
            user_data = data.get('user_data')
            if user_data and user_data.get('email'):
                try:
                    user = User.objects.get(email=user_data['email'])
                except User.DoesNotExist:
                    # Create a temporary user for anonymous mood tracking
                    user = User.objects.create_user(
                        username=f"anonymous_{user_data['email']}",
                        email=user_data['email'],
                        first_name=user_data.get('username', 'Anonymous'),
                        is_active=False  # Mark as inactive since it's anonymous
                    )
        
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'User authentication required'
            }, status=401)
        
        # Combine reasons and custom reason
        reason_text = ''
        if reasons:
            reason_text += ', '.join(reasons)
        if custom_reason:
            if reason_text:
                reason_text += f' | Custom: {custom_reason}'
            else:
                reason_text = f'Custom: {custom_reason}'
        
        # Save mood entry to database
        from .models import MoodEntry
        mood_entry = MoodEntry.objects.create(
            user=user,
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

@csrf_exempt
@require_http_methods(["GET"])
def get_mood_history_api(request):
    """Get mood history for the current user"""
    try:
        # Get user from request (if authenticated)
        user = None
        if request.user.is_authenticated:
            user = request.user
        else:
            # For anonymous users, try to get user from query parameters
            email = request.GET.get('email')
            if email:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'User not found'
                    }, status=404)
        
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'User authentication required'
            }, status=401)
        
        # Get mood entries for the user
        from .models import MoodEntry
        mood_entries = MoodEntry.objects.filter(user=user).order_by('-created_at')
        
        # Convert to JSON format
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

@csrf_exempt
@require_http_methods(["POST"])
def signup_api(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        institution_name = data.get('institution')
        role = data.get('role', 'student')

        if not all([username, email, password, institution_name]):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Username already exists. Please choose a different username.'}, status=400)

        institution, _ = Institution.objects.get_or_create(name=institution_name)

        # Create Django user
        django_user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        if role == 'admin':
            django_user.is_staff = True
            django_user.is_superuser = True
            django_user.save()

        # Create profile
        profile = UserProfile.objects.create(
            user=django_user,
            institution=institution,
            role=role
        )

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
                'institution': profile.institution.name
            },
            'redirect_url': '/mindcare-home/'
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
        if user_auth:
            django_login(request, user_auth)
            profile = UserProfile.objects.get(user=user_auth)
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'email': user_auth.email,
                    'username': user_auth.username,
                    'role': profile.role,
                    'institution': profile.institution.name
                },
                'redirect_url': '/mindcare-home/'
            })
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def logout_api(request):
    from django.contrib.auth import logout
    logout(request)
    return JsonResponse({'success': True, 'message': 'Logged out successfully'})


@csrf_exempt
def healthz(request):
    """Health check endpoint for environment and database validation"""
    health_status = {
        'status': 'ok',
        'env_ok': True,
        'db_ok': True,
        'supabase_ok': True,
        'gemini_ok': True,
        'details': {}
    }
    
    # Check environment variables
    try:
        env_details = {
            'debug': settings.DEBUG,
            'database_configured': bool(settings.DATABASES['default'].get('NAME') != 'db.sqlite3' or 
                                      settings.DATABASES['default'].get('ENGINE') == 'django.db.backends.postgresql'),
            'supabase_configured': bool(settings.SUPABASE_URL),
            'gemini_configured': bool(settings.GEMINI_API_KEY),
        }
        health_status['details']['environment'] = env_details
        
        if not settings.SUPABASE_URL:
            health_status['supabase_ok'] = False
            health_status['details']['supabase_error'] = 'SUPABASE_URL not configured'
            
        if not settings.GEMINI_API_KEY:
            health_status['gemini_ok'] = False
            health_status['details']['gemini_error'] = 'GEMINI_API_KEY not configured'
            
    except Exception as e:
        health_status['env_ok'] = False
        health_status['details']['env_error'] = str(e)
        logger.error(f"Environment check failed: {e}")
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            health_status['details']['database'] = {
                'engine': settings.DATABASES['default']['ENGINE'],
                'connected': True
            }
    except Exception as e:
        health_status['db_ok'] = False
        health_status['details']['database_error'] = str(e)
        logger.error(f"Database check failed: {e}")
    
    # Check Supabase connectivity (if configured)
    if settings.SUPABASE_URL and SUPABASE_AVAILABLE:
        try:
            supabase = get_supabase_client()
            # Simple test query
            result = supabase.table('base_userprofile').select('id').limit(1).execute()
            health_status['details']['supabase'] = {
                'url_configured': True,
                'connection_test': 'passed'
            }
        except Exception as e:
            health_status['supabase_ok'] = False
            health_status['details']['supabase_error'] = str(e)
            logger.error(f"Supabase check failed: {e}")
    
    # Overall status
    if not (health_status['env_ok'] and health_status['db_ok']):
        health_status['status'] = 'error'
    
    return JsonResponse(health_status, status=200 if health_status['status'] == 'ok' else 500)

def test_env_vars(request):
    """Test endpoint to check environment variables on Render"""
    import os
    
    # Check if we're in production
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
    
    # Try to import gemini_config to see what happens
    try:
        from gemini_config import GEMINI_AVAILABLE as GEMINI_AVAILABLE_IMPORT
        debug_info['gemini_config_status']['GEMINI_AVAILABLE_IMPORT'] = GEMINI_AVAILABLE_IMPORT
    except Exception as e:
        debug_info['gemini_config_status']['import_error'] = str(e)
    
    return JsonResponse(debug_info, status=200)

def simple_env_test(request):
    """Very simple environment test - just show raw env vars"""
    import os
    
    # Get all environment variables that start with our prefixes
    relevant_vars = {}
    for key, value in os.environ.items():
        if any(key.startswith(prefix) for prefix in ['GEMINI', 'SUPABASE', 'DATABASE', 'DEBUG', 'ALLOWED']):
            if 'KEY' in key or 'URL' in key:
                # Mask sensitive values
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
        'all_env_vars': dict(os.environ),  # Show ALL environment variables
    }, status=200)

def manual_env_setup(request):
    """Manual environment setup for testing"""
    import os
    
    # Manually set the environment variables for testing
    test_gemini_key = "AIzaSyDuELzG5dFcRox6UDAhML6DOUEh2-d232E"
    os.environ['GEMINI_API_KEY'] = test_gemini_key
    
    return JsonResponse({
        'message': 'Manually set GEMINI_API_KEY for testing',
        'gemini_key_set': bool(os.getenv('GEMINI_API_KEY')),
        'gemini_key_value': os.getenv('GEMINI_API_KEY', '')[:10] + "..." + os.getenv('GEMINI_API_KEY', '')[-4:] if os.getenv('GEMINI_API_KEY') else 'NOT SET',
    }, status=200)

def healthz(request):
    """Health check endpoint - no auth required"""
    from django.db import connection
    
    # Check environment variables
    env_ok = bool(settings.SUPABASE_URL and settings.GEMINI_API_KEY)
    
    # Check database connectivity
    db_ok = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
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

@require_http_methods(["POST"])
def gemini_chat_api(request):
    """Handle AI chat requests using Gemini API"""
    try:
        # Import functions locally to avoid import issues
        try:
            from gemini_config import generate_mental_health_response, is_mental_health_related, get_off_topic_response
        except ImportError as e:
            # Use fallback implementation when Google module is not available
            from gemini_fallback import generate_mental_health_response, is_mental_health_related, get_off_topic_response
        
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_history = data.get('conversation_history', [])
        
        # Debug: Log conversation history length
        print(f"Received message: '{user_message}' with {len(conversation_history)} previous messages")
        print(f"Conversation history: {conversation_history}")
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            }, status=400)
        
        # Check if message is mental health related
        if not is_mental_health_related(user_message):
            response_data = get_off_topic_response()
            return JsonResponse({
                'success': True,
                'response': response_data['text'],
                'safety_flags': response_data.get('safety_flags', []),
                'redirect': response_data.get('redirect', False),
                'model': 'gemini-mental-health-filter'
            })
        
        # Generate response using Gemini
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



def analytics_dashboard(request):
    """Analytics dashboard view - admin only"""
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            # Check if user is admin - check role and user email
            if (user_profile.role == 'admin' or 
                user_profile.user.email == 'admin@test.com' or
                user_profile.user.email == 'admin@demo.com' or
                user_profile.user.username == 'admin@test.com'):
                return render(request, 'analytics_dashboard.html')
            else:
                messages.error(request, 'Access denied. Admin privileges required.')
                return redirect('mindcare_home')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found')
            return redirect('login')
    else:
        return redirect('login')

def database_viewer(request):
    """Database viewer - admin only"""
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            # Check if user is admin
            if (user_profile.role == 'admin' or 
                user_profile.user.email == 'admin@test.com' or
                user_profile.user.email == 'admin@demo.com' or
                user_profile.user.username == 'admin@test.com' or
                request.user.is_superuser):
                
                from django.contrib.auth.models import User
                
                from .models import MoodEntry
                context = {
                    'users': User.objects.all(),
                    'profiles': UserProfile.objects.all(),
                    'institutions': Institution.objects.all(),
                    'mood_entries': MoodEntry.objects.all()[:20],  # Show last 20 entries
                    'total_users': User.objects.count(),
                    'total_profiles': UserProfile.objects.count(),
                    'total_institutions': Institution.objects.count(),
                    'total_mood_entries': MoodEntry.objects.count(),
                    'admin_users': User.objects.filter(is_superuser=True).count(),
                }
                return render(request, 'database_viewer.html', context)
            else:
                messages.error(request, 'Access denied. Admin privileges required.')
                return redirect('mindcare_home')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found')
            return redirect('login')
    else:
        return redirect('login')