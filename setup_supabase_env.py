#!/usr/bin/env python3
"""
Setup script to create .env file for Supabase configuration
"""
import os

def create_env_file():
    """Create .env file with Supabase configuration template"""
    
    env_content = """# Supabase Configuration
# Replace these with your actual Supabase project credentials
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Django Configuration
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True

# Database Configuration (for Supabase PostgreSQL)
# Uncomment and configure these when you want to use Supabase database
# DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file template")
        print("📝 Please edit .env file with your actual Supabase credentials")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def show_supabase_setup_instructions():
    """Show instructions for setting up Supabase"""
    print("\n" + "="*60)
    print("🔧 SUPABASE SETUP INSTRUCTIONS")
    print("="*60)
    print("\n1. Go to https://supabase.com and sign in")
    print("2. Create a new project or select existing project")
    print("3. Go to Settings → API")
    print("4. Copy your Project URL and API keys")
    print("5. Edit the .env file with your credentials:")
    print("\n   SUPABASE_URL=https://your-project-id.supabase.co")
    print("   SUPABASE_ANON_KEY=your_anon_key_here")
    print("   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here")
    print("\n6. Run: python manage.py migrate")
    print("7. Your mood data will then be stored in Supabase!")
    print("\n" + "="*60)

if __name__ == "__main__":
    print("🚀 Setting up Supabase environment configuration...")
    
    if create_env_file():
        show_supabase_setup_instructions()
    else:
        print("❌ Failed to create .env file")
