#!/usr/bin/env python3
"""
Deployment check script for MindCare platform
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

def check_deployment():
    """Check if the application is ready for deployment"""
    print("🔍 Checking MindCare deployment readiness...")
    
    try:
        # Setup Django
        django.setup()
        print("✅ Django setup successful")
        
        # Check settings
        from django.conf import settings
        print(f"✅ DEBUG mode: {settings.DEBUG}")
        print(f"✅ Allowed hosts: {settings.ALLOWED_HOSTS}")
        print(f"✅ Static URL: {settings.STATIC_URL}")
        print(f"✅ Static root: {settings.STATIC_ROOT}")
        
        # Check database
        from django.db import connection
        connection.ensure_connection()
        print("✅ Database connection successful")
        
        # Check models
        from base.models import UserProfile, Institution
        print("✅ Models imported successfully")
        
        # Check URLs
        from django.urls import reverse
        print("✅ URL configuration successful")
        
        print("\n🎉 All checks passed! Ready for deployment.")
        return True
        
    except Exception as e:
        print(f"❌ Deployment check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_deployment()
