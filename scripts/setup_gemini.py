#!/usr/bin/env python3
"""
Gemini API Setup Script
This script helps you set up the Gemini API key for the MindCare platform
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has Gemini API key"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found")
        return False, None
    
    with open(env_path, 'r') as f:
        content = f.read()
        
    if 'GEMINI_API_KEY' in content:
        print("✅ GEMINI_API_KEY found in .env file")
        return True, content
    else:
        print("⚠️ GEMINI_API_KEY not found in .env file")
        return False, content

def add_gemini_key_to_env():
    """Add Gemini API key to .env file"""
    env_path = Path('.env')
    
    print("\n🔑 Gemini API Key Setup")
    print("=" * 50)
    print("To get your Gemini API key:")
    print("1. Go to https://aistudio.google.com/")
    print("2. Sign in with your Google account")
    print("3. Click 'Get API Key' in the left sidebar")
    print("4. Create a new API key")
    print("5. Copy the API key (starts with 'AIza...')")
    print()
    
    api_key = input("Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
        
    if not api_key.startswith('AIza'):
        print("⚠️ Warning: API key doesn't start with 'AIza'. Please verify it's correct.")
        confirm = input("Continue anyway? (y/n): ").lower()
        if confirm != 'y':
            return False
    
    # Read existing .env content
    existing_content = ""
    if env_path.exists():
        with open(env_path, 'r') as f:
            existing_content = f.read()
    
    # Add or update GEMINI_API_KEY
    if 'GEMINI_API_KEY' in existing_content:
        # Update existing key
        lines = existing_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('GEMINI_API_KEY='):
                lines[i] = f'GEMINI_API_KEY={api_key}'
                break
        new_content = '\n'.join(lines)
    else:
        # Add new key
        if existing_content and not existing_content.endswith('\n'):
            existing_content += '\n'
        new_content = existing_content + f'GEMINI_API_KEY={api_key}\n'
    
    # Write updated content
    with open(env_path, 'w') as f:
        f.write(new_content)
    
    print("✅ Gemini API key added to .env file")
    return True

def test_gemini_connection():
    """Test the Gemini API connection"""
    print("\n🧪 Testing Gemini API Connection...")
    
    try:
        from dotenv import load_dotenv
        import google.generativeai as genai
        
        # Load environment variables
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Test with a simple query
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, this is a test message.")
        
        if response.text:
            print("✅ Gemini API connection successful!")
            print(f"📝 Test response: {response.text[:100]}...")
            return True
        else:
            print("❌ No response from Gemini API")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemini connection: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 MindCare Gemini API Setup")
    print("=" * 50)
    
    # Check current status
    has_key, env_content = check_env_file()
    
    if not has_key:
        print("\n📝 Setting up Gemini API key...")
        if not add_gemini_key_to_env():
            print("❌ Setup cancelled")
            return
        
        # Test the connection
        if test_gemini_connection():
            print("\n🎉 Setup complete! Gemini API is ready to use.")
            print("\nNext steps:")
            print("1. Start your Django server: python manage.py runserver")
            print("2. Navigate to the AI Support page")
            print("3. Test the chatbot with mental health queries")
        else:
            print("\n⚠️ Setup completed but API test failed.")
            print("Please check your API key and try again.")
    else:
        print("\n🔍 Testing existing Gemini API key...")
        if test_gemini_connection():
            print("✅ Gemini API is already working correctly!")
        else:
            print("❌ Existing API key is not working.")
            print("You may need to update it.")
            
            update = input("Update the API key? (y/n): ").lower()
            if update == 'y':
                add_gemini_key_to_env()
                test_gemini_connection()

if __name__ == "__main__":
    main()
