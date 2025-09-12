#!/usr/bin/env python3
"""
Deployment helper script for VidSnap-AI
"""

import os
import subprocess
import sys

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'main.py',
        'requirements.txt',
        'Procfile',
        'templates/',
        'static/',
        'config.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present")
    return True

def check_environment():
    """Check environment variables"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found. Creating template...")
        with open('.env', 'w') as f:
            f.write("ELEVENLABS_API_KEY=your_api_key_here\n")
        print("📝 Please edit .env file with your actual API key")
        return False
    
    print("✅ Environment file found")
    return True

def test_application():
    """Test if the application runs"""
    try:
        print("🧪 Testing application...")
        result = subprocess.run([sys.executable, '-c', 'import main; print("App imports successfully")'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Application test passed")
            return True
        else:
            print(f"❌ Application test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Application test error: {e}")
        return False

def main():
    """Main deployment check"""
    print("🚀 VidSnap-AI Deployment Check")
    print("=" * 40)
    
    checks = [
        ("File Check", check_requirements),
        ("Environment Check", check_environment),
        ("Application Test", test_application)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All checks passed! Ready for deployment!")
        print("\n📚 Next steps:")
        print("1. Push your code to GitHub")
        print("2. Connect to your deployment platform (Railway/Render/Heroku)")
        print("3. Set environment variables on your platform")
        print("4. Deploy!")
    else:
        print("❌ Some checks failed. Please fix the issues above before deploying.")
    
    return all_passed

if __name__ == "__main__":
    main()
