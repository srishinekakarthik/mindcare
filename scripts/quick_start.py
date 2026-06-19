#!/usr/bin/env python
"""
Quick start script for Supabase integration
This script helps you get started quickly with the Supabase integration
"""

import os
import sys

def create_env_file():
    """Create .env file with user input"""
    print("🚀 Supabase Integration Quick Start")
    print("=" * 40)
    
    print("\n📋 You'll need your Supabase project credentials:")
    print("1. Go to https://supabase.com")
    print("2. Create a new project or select existing one")
    print("3. Go to Settings → API")
    print("4. Copy your Project URL and API keys")
    
    print("\n🔧 Let's set up your environment variables:")
    
    supabase_url = input("\nEnter your Supabase Project URL: ").strip()
    if not supabase_url:
        print("❌ Project URL is required!")
        return False
    
    anon_key = input("Enter your Supabase Anon Key: ").strip()
    if not anon_key:
        print("❌ Anon Key is required!")
        return False
    
    service_key = input("Enter your Supabase Service Role Key: ").strip()
    if not service_key:
        print("❌ Service Role Key is required!")
        return False
    
    # Create .env file
    env_content = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_ANON_KEY={anon_key}
SUPABASE_SERVICE_ROLE_KEY={service_key}

# Django Configuration
SECRET_KEY=django-insecure-e8%q@h1rxa8tp7r)m91u(7it5wwhe3(e-8uz00!*-d1st7drl%
DEBUG=True
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ .env file created successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Failed to create .env file: {e}")
        return False

def update_html_templates():
    """Update HTML templates with Supabase credentials"""
    print("\n🔧 Updating HTML templates...")
    
    # Read .env file to get credentials
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        # Extract values
        supabase_url = None
        anon_key = None
        
        for line in env_content.split('\n'):
            if line.startswith('SUPABASE_URL='):
                supabase_url = line.split('=', 1)[1]
            elif line.startswith('SUPABASE_ANON_KEY='):
                anon_key = line.split('=', 1)[1]
        
        if not supabase_url or not anon_key:
            print("❌ Could not extract credentials from .env file")
            return False
        
        # Update login.html
        try:
            with open('templates/login.html', 'r') as f:
                login_content = f.read()
            
            login_content = login_content.replace(
                "const SUPABASE_URL = 'your_supabase_project_url';",
                f"const SUPABASE_URL = '{supabase_url}';"
            )
            login_content = login_content.replace(
                "const SUPABASE_ANON_KEY = 'your_supabase_anon_key';",
                f"const SUPABASE_ANON_KEY = '{anon_key}';"
            )
            
            with open('templates/login.html', 'w') as f:
                f.write(login_content)
            
            print("✅ Updated login.html")
        except Exception as e:
            print(f"❌ Failed to update login.html: {e}")
            return False
        
        # Update signup.html
        try:
            with open('templates/signup.html', 'r') as f:
                signup_content = f.read()
            
            signup_content = signup_content.replace(
                "const SUPABASE_URL = 'your_supabase_project_url';",
                f"const SUPABASE_URL = '{supabase_url}';"
            )
            signup_content = signup_content.replace(
                "const SUPABASE_ANON_KEY = 'your_supabase_anon_key';",
                f"const SUPABASE_ANON_KEY = '{anon_key}';"
            )
            
            with open('templates/signup.html', 'w') as f:
                f.write(signup_content)
            
            print("✅ Updated signup.html")
        except Exception as e:
            print(f"❌ Failed to update signup.html: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update templates: {e}")
        return False

def run_tests():
    """Run integration tests"""
    print("\n🧪 Running integration tests...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'test_supabase_integration.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def main():
    """Main quick start function"""
    print("🎯 Supabase Integration Quick Start")
    print("This script will help you set up Supabase integration quickly.\n")
    
    # Check if .env already exists
    if os.path.exists('.env'):
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Setup cancelled.")
            return
    
    # Step 1: Create .env file
    if not create_env_file():
        print("❌ Setup failed at environment configuration.")
        return
    
    # Step 2: Update HTML templates
    if not update_html_templates():
        print("❌ Setup failed at template updates.")
        return
    
    # Step 3: Run tests
    if not run_tests():
        print("❌ Setup completed but tests failed. Please check your configuration.")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Run: python manage.py runserver")
    print("2. Visit: http://localhost:8000/admin-student-portal/")
    print("3. Test the signup and login functionality")
    print("\n📚 For detailed documentation, see: SUPABASE_SETUP_GUIDE.md")

if __name__ == "__main__":
    main()
