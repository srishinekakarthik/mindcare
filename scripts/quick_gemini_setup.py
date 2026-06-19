#!/usr/bin/env python3
"""
Quick Gemini API Setup Script
This script helps you quickly set up the Gemini API key
"""

import os
from pathlib import Path

def main():
    print("🚀 Quick Gemini API Setup")
    print("=" * 40)
    
    # Check if .env exists
    env_path = Path('.env')
    
    if env_path.exists():
        print("✅ .env file found")
        with open(env_path, 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY' in content and 'your-gemini-api-key-here' not in content:
                print("✅ GEMINI_API_KEY already configured")
                return
    else:
        print("📝 Creating .env file...")
        # Create basic .env file
        with open(env_path, 'w') as f:
            f.write("""# Django Configuration
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# Supabase Configuration (if you have these)
# SUPABASE_URL=https://your-project-id.supabase.co
# SUPABASE_ANON_KEY=your-supabase-anon-key
# SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Gemini API Configuration
GEMINI_API_KEY=your-gemini-api-key-here
""")
        print("✅ .env file created")
    
    print("\n🔑 To get your Gemini API key:")
    print("1. Go to: https://aistudio.google.com/")
    print("2. Sign in with Google account")
    print("3. Click 'Get API Key'")
    print("4. Create new API key")
    print("5. Copy the key (starts with 'AIza...')")
    print()
    
    api_key = input("Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return
    
    # Update .env file
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Replace the placeholder
    updated_content = content.replace('GEMINI_API_KEY=your-gemini-api-key-here', f'GEMINI_API_KEY={api_key}')
    
    with open(env_path, 'w') as f:
        f.write(updated_content)
    
    print("✅ API key saved to .env file")
    print("\n🧪 Testing connection...")
    
    # Test the connection
    try:
        from dotenv import load_dotenv
        import google.generativeai as genai
        
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Hello, this is a test.")
            
            if response.text:
                print("✅ Gemini API connection successful!")
                print("🎉 Setup complete! Your chatbot is now ready.")
                print("\nNext steps:")
                print("1. Start your Django server: python manage.py runserver")
                print("2. Go to the AI Support page")
                print("3. Test the chatbot with mental health queries")
            else:
                print("❌ No response from Gemini API")
        else:
            print("❌ API key not found in environment")
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main()
