#!/usr/bin/env python
"""
Update Supabase configuration in HTML templates
"""

import os
from dotenv import load_dotenv

def update_html_templates():
    """Update HTML templates with actual Supabase credentials"""
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not anon_key:
        print("❌ Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file first")
        return False
    
    if supabase_url == 'https://your-project-id.supabase.co' or anon_key == 'your_anon_key_here':
        print("❌ Please update your .env file with actual Supabase credentials")
        return False
    
    print(f"✅ Found Supabase URL: {supabase_url}")
    print(f"✅ Found Anon Key: {anon_key[:20]}...")
    
    # Update signup.html
    try:
        with open('templates/signup.html', 'r') as f:
            content = f.read()
        
        content = content.replace(
            "const SUPABASE_URL = 'https://your-actual-project-id.supabase.co';",
            f"const SUPABASE_URL = '{supabase_url}';"
        )
        content = content.replace(
            "const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';",
            f"const SUPABASE_ANON_KEY = '{anon_key}';"
        )
        
        with open('templates/signup.html', 'w') as f:
            f.write(content)
        
        print("✅ Updated templates/signup.html")
    except Exception as e:
        print(f"❌ Failed to update signup.html: {e}")
        return False
    
    # Update login.html
    try:
        with open('templates/login.html', 'r') as f:
            content = f.read()
        
        content = content.replace(
            "const SUPABASE_URL = 'https://your-actual-project-id.supabase.co';",
            f"const SUPABASE_URL = '{supabase_url}';"
        )
        content = content.replace(
            "const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';",
            f"const SUPABASE_ANON_KEY = '{anon_key}';"
        )
        
        with open('templates/login.html', 'w') as f:
            f.write(content)
        
        print("✅ Updated templates/login.html")
    except Exception as e:
        print(f"❌ Failed to update login.html: {e}")
        return False
    
    return True

def main():
    print("🔧 Updating Supabase Configuration")
    print("=" * 40)
    
    if update_html_templates():
        print("\n🎉 Configuration updated successfully!")
        print("\n📝 Next steps:")
        print("1. Restart your Django server: python manage.py runserver")
        print("2. Test the connection: python test_supabase_integration.py")
        print("3. Visit: http://127.0.0.1:8000/admin-student-portal/")
    else:
        print("\n❌ Configuration update failed")
        print("\n🔧 Please check your .env file and try again")

if __name__ == "__main__":
    main()
