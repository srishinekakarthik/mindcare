#!/usr/bin/env python3
"""
Database viewer script for MindCare platform
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
django.setup()

from django.contrib.auth.models import User
from base.models import UserProfile, Institution, MoodEntry

def view_database():
    """View all database contents"""
    print("🗄️ MindCare Database Contents")
    print("=" * 50)
    
    # Users
    print(f"\n👥 USERS ({User.objects.count()} total)")
    print("-" * 30)
    for user in User.objects.all():
        print(f"ID: {user.id} | Username: {user.username} | Email: {user.email}")
        print(f"   First Name: {user.first_name} | Last Name: {user.last_name}")
        print(f"   Is Admin: {user.is_superuser} | Is Staff: {user.is_staff}")
        print(f"   Date Joined: {user.date_joined}")
        print()
    
    # User Profiles
    print(f"\n👤 USER PROFILES ({UserProfile.objects.count()} total)")
    print("-" * 30)
    for profile in UserProfile.objects.all():
        print(f"ID: {profile.id} | User: {profile.user.username}")
        print(f"   Role: {profile.role} | Institution: {profile.institution.name}")
        print(f"   Supabase ID: {profile.supabase_user_id}")
        print(f"   Created: {profile.created_at}")
        print()
    
    # Institutions
    print(f"\n🏫 INSTITUTIONS ({Institution.objects.count()} total)")
    print("-" * 30)
    for institution in Institution.objects.all():
        print(f"ID: {institution.id} | Name: {institution.name}")
        print(f"   Created: {institution.created_at}")
        print()
    
    # Summary
    print("\n📊 SUMMARY")
    print("-" * 30)
    print(f"Total Users: {User.objects.count()}")
    print(f"Total User Profiles: {UserProfile.objects.count()}")
    print(f"Total Institutions: {Institution.objects.count()}")
    print(f"Total Mood Entries: {MoodEntry.objects.count()}")
    print(f"Admin Users: {User.objects.filter(is_superuser=True).count()}")
    print(f"Staff Users: {User.objects.filter(is_staff=True).count()}")

def view_specific_data():
    """View specific data with more details"""
    print("\n🔍 DETAILED VIEW")
    print("=" * 50)
    
    # Show admin users
    admin_users = User.objects.filter(is_superuser=True)
    if admin_users:
        print(f"\n🔑 ADMIN USERS ({admin_users.count()})")
        for user in admin_users:
            print(f"   {user.username} ({user.email})")
    
    # Show user profiles with roles
    profiles = UserProfile.objects.all()
    if profiles:
        print(f"\n👤 USER PROFILES BY ROLE")
        for profile in profiles:
            print(f"   {profile.user.username}: {profile.role} at {profile.institution.name}")
        
        print("\n😊 MOOD ENTRIES")
        print("-" * 30)
        mood_entries = MoodEntry.objects.all().order_by('-created_at')
        if mood_entries:
            for entry in mood_entries:
                print(f"ID: {entry.id} | User: {entry.user.username}")
                print(f"   Mood: {entry.mood_label} (Value: {entry.mood_value})")
                print(f"   Reason: {entry.reason}")
                print(f"   Created: {entry.created_at.strftime('%Y-%m-%d %H:%M')}")
                print()
        else:
            print("   No mood entries found")

if __name__ == "__main__":
    try:
        view_database()
        view_specific_data()
        print("\n✅ Database view completed successfully!")
    except Exception as e:
        print(f"❌ Error viewing database: {e}")
        import traceback
        traceback.print_exc()
