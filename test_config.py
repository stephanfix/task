#!/usr/bin/env python3
"""
test_config.py - Test configuration management setup

Run this script to verify your configuration is working:
    python test_config.py
"""

from dotenv import load_dotenv
import os
from pathlib import Path

def test_environment_loading():
    """Test that environment variables load correctly"""
    print("🔍 Testing Configuration Management")
    print("=" * 50)
    
    # Test 1: Check if .env files exist
    print("\n1️⃣ Checking for .env files...")
    
    files_to_check = [
        'user_service/.env.development',
        'task_service/.env.development',
        'frontend/.env.development',
        '.env'
    ]
    
    missing_files = []
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"   ✅ Found: {file_path}")
        else:
            print(f"   ❌ Missing: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Warning: {len(missing_files)} file(s) missing")
        print("   Create them using the provided templates!")
    
    # Test 2: Load and display user service config
    print("\n2️⃣ Testing User Service Configuration...")
    load_dotenv('user_service/.env.development')
    
    user_config = {
        'FLASK_ENV': os.getenv('FLASK_ENV', 'NOT SET'),
        'DEBUG': os.getenv('DEBUG', 'NOT SET'),
        'DATABASE': os.getenv('DATABASE', 'NOT SET'),
        'PORT': os.getenv('PORT', 'NOT SET'),
        'SECRET_KEY': '***' if os.getenv('SECRET_KEY') else 'NOT SET'
    }
    
    for key, value in user_config.items():
        status = "✅" if value != "NOT SET" else "❌"
        print(f"   {status} {key}: {value}")
    
    # Test 3: Load and display task service config
    print("\n3️⃣ Testing Task Service Configuration...")
    load_dotenv('task_service/.env.development')
    
    task_config = {
        'FLASK_ENV': os.getenv('FLASK_ENV', 'NOT SET'),
        'DEBUG': os.getenv('DEBUG', 'NOT SET'),
        'DATABASE': os.getenv('DATABASE', 'NOT SET'),
        'PORT': os.getenv('PORT', 'NOT SET'),
        'USER_SERVICE_URL': os.getenv('USER_SERVICE_URL', 'NOT SET')
    }
    
    for key, value in task_config.items():
        status = "✅" if value != "NOT SET" else "❌"
        print(f"   {status} {key}: {value}")
    
    # Test 4: Check .gitignore
    print("\n4️⃣ Checking .gitignore...")
    if Path('.gitignore').exists():
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            
        if '.env' in gitignore_content:
            print("   ✅ .env files are in .gitignore")
        else:
            print("   ⚠️  WARNING: .env not found in .gitignore!")
            print("   Add this to prevent committing secrets!")
    else:
        print("   ❌ No .gitignore found!")
    
    # Test 5: Check data directories
    print("\n5️⃣ Checking data directories...")
    data_dirs = ['data/user_service', 'data/task_service']
    
    for dir_path in data_dirs:
        if Path(dir_path).exists():
            print(f"   ✅ {dir_path} exists")
        else:
            print(f"   ℹ️  {dir_path} doesn't exist (will be created on first run)")
    
    # Summary
    print("\n" + "=" * 50)
    print("✅ Configuration test complete!")
    print("\nNext steps:")
    print("1. Fix any ❌ issues above")
    print("2. Create missing .env files from .env.example")
    print("3. Run your services: python user_service/app.py")
    print("=" * 50)


def test_config_classes():
    """Test that config classes work correctly"""
    print("\n🧪 Testing Configuration Classes")
    print("=" * 50)
    
    try:
        # Import config from user service
        import sys
        sys.path.insert(0, str(Path('user_service').resolve()))
        from config import get_config, DevelopmentConfig, ProductionConfig
        
        print("\n1️⃣ Development Config:")
        dev_config = DevelopmentConfig()
        print(f"   Debug: {dev_config.DEBUG}")
        print(f"   Database: {dev_config.DATABASE_PATH}")
        
        print("\n2️⃣ Production Config:")
        prod_config = ProductionConfig()
        print(f"   Debug: {prod_config.DEBUG}")
        print(f"   Database: {prod_config.DATABASE_PATH}")
        
        print("\n✅ Config classes working correctly!")
        
    except ImportError as e:
        print(f"\n❌ Error importing config: {e}")
        print("   Make sure you've created the config.py files!")
    except Exception as e:
        print(f"\n❌ Error testing config: {e}")


if __name__ == '__main__':
    test_environment_loading()
    test_config_classes()
    
    print("\n💡 Pro tip: Run this script whenever you change configuration!")
    print("   python test_config.py")