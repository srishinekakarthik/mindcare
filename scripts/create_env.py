#!/usr/bin/env python3
"""
Create .env file with proper Gemini API key
"""

def create_env_file():
    print("🔧 Creating .env file...")
    
    # Get API key from user
    print("\n🔑 Please get your Gemini API key:")
    print("1. Go to: https://aistudio.google.com/")
    print("2. Sign in with Google account")
    print("3. Click 'Get API Key'")
    print("4. Create new API key")
    print("5. Copy the key (starts with 'AIza...')")
    print()
    
    api_key = input("Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    # Create .env content
    env_content = f"""# Django Configuration
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# Supabase Configuration (if you have these)
# SUPABASE_URL=https://your-project-id.supabase.co
# SUPABASE_ANON_KEY=your-supabase-anon-key
# SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Gemini API Configuration
GEMINI_API_KEY={api_key}
"""
    
    # Write to .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

if __name__ == "__main__":
    create_env_file()
