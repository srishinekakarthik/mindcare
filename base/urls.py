from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin-student-portal/', views.home, name='admin-student-portal'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('database/', views.database_viewer, name='database_viewer'),
    path('mindcare-home/', views.mindcare_home, name='mindcare_home'),
    path('ai-support/', views.ai_support, name='ai_support'),
    path('book-session/', views.book_session, name='book_session'),
    path('self-assessment/', views.self_assessment, name='self_assessment'),
    path('mood-tracker/', views.mood_tracker, name='mood_tracker'),
    path('peer-support/', views.peer_support, name='peer_support'),
    path('resources/', views.resources, name='resources'),
    
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
    path('api/gemini-chat/', views.gemini_chat_api, name='gemini_chat_api'),
]
