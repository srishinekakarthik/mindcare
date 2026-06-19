import os
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

# Supabase configuration using centralized settings
try:
    from django.conf import settings
    SUPABASE_URL = settings.SUPABASE_URL
    SUPABASE_ANON_KEY = settings.SUPABASE_ANON_KEY
    SUPABASE_SERVICE_ROLE_KEY = settings.SUPABASE_SERVICE_ROLE_KEY
except ImportError:
    # Fallback for when Django settings are not available
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')
    SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

def get_supabase_client() -> Client:
    """Create and return a Supabase client instance"""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_supabase_admin_client() -> Client:
    """Create and return a Supabase admin client with service role key"""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
