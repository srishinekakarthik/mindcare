#!/usr/bin/env python3
"""
Simple deployment helper script
This will help you prepare your code for Render deployment
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and show the result"""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ ERROR: {description}")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    print("🚀 RENDER DEPLOYMENT HELPER")
    print("=" * 50)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository. Please run 'git init' first.")
        return
    
    # Check git status
    print("\n📋 Checking git status...")
    run_command("git status", "Git status check")
    
    # Add all files
    print("\n📁 Adding files to git...")
    run_command("git add .", "Add all files to git")
    
    # Check what will be committed
    print("\n📋 Files to be committed:")
    run_command("git status --porcelain", "Show staged files")
    
    # Commit changes
    commit_message = input("\n💬 Enter commit message (or press Enter for default): ").strip()
    if not commit_message:
        commit_message = "Deploy to Render with environment testing"
    
    success = run_command(f'git commit -m "{commit_message}"', "Commit changes")
    
    if not success:
        print("❌ Commit failed. Please check the errors above.")
        return
    
    # Push to GitHub
    print("\n🌐 Pushing to GitHub...")
    success = run_command("git push origin main", "Push to GitHub")
    
    if success:
        print("\n🎉 SUCCESS! Your code has been pushed to GitHub.")
        print("\n📋 NEXT STEPS:")
        print("1. Go to your Render dashboard")
        print("2. Set up environment variables (see instructions below)")
        print("3. Deploy your service")
        print("4. Test the endpoints:")
        print("   - https://your-app.onrender.com/healthz/")
        print("   - https://your-app.onrender.com/test-env/")
    else:
        print("\n❌ Push failed. Please check your GitHub connection.")

if __name__ == "__main__":
    main()
