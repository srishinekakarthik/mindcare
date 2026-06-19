"""
Centralized environment variable loading and validation for Django project.
Handles environment variables for both local development and production deployment.
"""

import os
import re
import logging

logger = logging.getLogger(__name__)

def get_env(key, default=""):
    """Get environment variable with whitespace trimming"""
    return os.getenv(key, default).strip()

def get_bool(key, default=False):
    """Get boolean environment variable"""
    value = os.getenv(key, "").strip().lower()
    return value in ('true', '1', 'yes', 'on')

def validate_supabase_url(url):
    """Validate and extract project reference from Supabase URL"""
    if not url:
        return None, None
    
    # Pattern: https://<ref>.supabase.co
    pattern = r'^https://([a-z0-9]{20,30})\.supabase\.co/?$'
    match = re.match(pattern, url)
    
    if not match:
        logger.error("Invalid SUPABASE_URL format. Expected: https://<ref>.supabase.co")
        return None, None
    
    project_ref = match.group(1)
    return url, project_ref

def normalize_database_url(url):
    """Normalize database URL and add SSL mode if needed"""
    if not url:
        return None
    
    # Strip whitespace
    url = url.strip()
    
    if not url:
        return None
    
    # Normalize postgres:// to postgresql://
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    
    # Add SSL mode if not present
    if '?' not in url:
        url += '?sslmode=require'
    elif 'sslmode=' not in url:
        url += '&sslmode=require'
    
    return url

def get_environment_config():
    """Get and validate all environment configuration"""
    config = {}
    
    # Core environment variables
    config['SUPABASE_URL'] = get_env('SUPABASE_URL')
    config['SUPABASE_ANON_KEY'] = get_env('SUPABASE_ANON_KEY')
    config['SUPABASE_SERVICE_ROLE_KEY'] = get_env('SUPABASE_SERVICE_ROLE_KEY')
    config['GEMINI_API_KEY'] = get_env('GEMINI_API_KEY')
    config['DATABASE_URL'] = get_env('DATABASE_URL')
    
    # Boolean settings
    config['DEBUG'] = get_bool('DEBUG', False)
    
    # ALLOWED_HOSTS configuration - always include Render domains
    default_hosts = 'localhost,127.0.0.1,testserver,mindcare-platform-1.onrender.com,mindcare-platform.onrender.com'
    allowed_hosts = get_env('ALLOWED_HOSTS', default_hosts)
    config['ALLOWED_HOSTS'] = [host.strip() for host in allowed_hosts.split(',') if host.strip()]
    
    # Validate Supabase URL
    if config['SUPABASE_URL']:
        validated_url, project_ref = validate_supabase_url(config['SUPABASE_URL'])
        if validated_url:
            config['SUPABASE_URL'] = validated_url
            config['SUPABASE_PROJECT_REF'] = project_ref
        else:
            config['SUPABASE_URL'] = None
            config['SUPABASE_PROJECT_REF'] = None
    else:
        config['SUPABASE_PROJECT_REF'] = None
    
    # Normalize database URL
    if config['DATABASE_URL']:
        config['DATABASE_URL'] = normalize_database_url(config['DATABASE_URL'])
    
    # Log missing environment variables (without revealing values)
    missing_vars = []
    if not config['SUPABASE_URL']:
        missing_vars.append('SUPABASE_URL')
    if not config['SUPABASE_ANON_KEY']:
        missing_vars.append('SUPABASE_ANON_KEY')
    if not config['GEMINI_API_KEY']:
        missing_vars.append('GEMINI_API_KEY')
    if not config['DATABASE_URL']:
        missing_vars.append('DATABASE_URL')
    
    if missing_vars:
        logger.warning(f"missing_env={missing_vars}")
    
    # Debug logging for ALLOWED_HOSTS
    logger.info(f"ALLOWED_HOSTS configured: {config['ALLOWED_HOSTS']}")
    
    return config

# Load configuration
ENV_CONFIG = get_environment_config()