from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('mindcare-home/', views.mindcare_home, name='mindcare_home'),
    path('ai-support/', views.ai_support, name='ai_support'),
    path('self-assessment/', views.self_assessment, name='self_assessment'),
    path('mood-tracker/', views.mood_tracker, name='mood_tracker'),
    path('peer-support/', views.peer_support, name='peer_support'),
    path('peer-support/<int:post_id>/comment/', views.peer_support_comment, name='peer_support_comment'),
    path('resources/', views.resources, name='resources'),
    path('resources/<int:resource_id>/', views.resource_detail, name='resource_detail'),

    # Booking (student-facing)
    path('book-session/', views.book_session, name='book_session'),
    path('book-session/<int:counselor_id>/slots/', views.counselor_slots_api, name='counselor_slots_api'),
    path('api/book-session/', views.create_booking_api, name='create_booking_api'),
    path('api/cancel-session/<int:session_id>/', views.cancel_session_api, name='cancel_session_api'),

    # Counselor-facing
    path('counselor/dashboard/', views.counselor_dashboard, name='counselor_dashboard'),
    path('counselor/availability/', views.counselor_availability, name='counselor_availability'),
    path('counselor/resources/', views.counselor_resources, name='counselor_resources'),
    path('api/counselor/availability/add/', views.add_availability_api, name='add_availability_api'),
    path('api/counselor/availability/<int:slot_id>/delete/', views.delete_availability_api, name='delete_availability_api'),
    path('api/counselor/session/<int:session_id>/complete/', views.complete_session_api, name='complete_session_api'),
    path('api/counselor/resources/add/', views.add_resource_api, name='add_resource_api'),

    # Admin-facing
    path('dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('database/', views.database_viewer, name='database_viewer'),
    path('admin-panel/counselors/', views.manage_counselors, name='manage_counselors'),
    path('api/admin/counselor/<int:profile_id>/approve/', views.approve_counselor_api, name='approve_counselor_api'),
    path('api/admin/counselor/<int:profile_id>/reject/', views.reject_counselor_api, name='reject_counselor_api'),

    # Health check endpoint
    path('healthz/', views.healthz, name='healthz'),
    path('env-debug/', views.env_debug, name='env_debug'),

    # Legacy debug endpoints
    path('test-env/', views.test_env_vars, name='test_env_vars'),
    path('debug-env/', views.debug_env_vars, name='debug_env_vars'),
    path('simple-env/', views.simple_env_test, name='simple_env_test'),
    path('manual-env/', views.manual_env_setup, name='manual_env_setup'),

    # API endpoints
    path('api/save-mood/', views.save_mood_api, name='save_mood_api'),
    path('api/mood-history/', views.get_mood_history_api, name='get_mood_history_api'),
    path('api/signup/', views.signup_api, name='signup_api'),
    path('api/login/', views.login_api, name='login_api'),
    path('api/logout/', views.logout_api, name='logout_api'),
    path('api/me/', views.current_user_api, name='current_user_api'),
    path('api/gemini-chat/', views.gemini_chat_api, name='gemini_chat_api'),
    path('api/submit-assessment/', views.submit_assessment_api, name='submit_assessment_api'),
    path('api/peer-support/create/', views.create_peer_post_api, name='create_peer_post_api'),
]
