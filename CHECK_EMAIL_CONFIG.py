#!/usr/bin/env python3
"""
Email Configuration Diagnostic Tool
Run this to verify email setup is correct before testing
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has email config"""
    print("\n" + "="*60)
    print("STEP 1: Checking .env File")
    print("="*60)
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file NOT FOUND")
        print("   Create .env file with: touch .env")
        return False
    
    print("✅ .env file exists")
    
    # Read .env file
    with open(".env", "r") as f:
        env_content = f.read()
    
    # Check for RESEND_API_KEY
    if "RESEND_API_KEY" not in env_content:
        print("❌ RESEND_API_KEY not found in .env")
        print("   Add this line to .env:")
        print("   RESEND_API_KEY=re_YOUR_ACTUAL_KEY")
        return False
    
    # Extract RESEND_API_KEY
    for line in env_content.split("\n"):
        if line.startswith("RESEND_API_KEY"):
            parts = line.split("=")
            if len(parts) == 2:
                api_key = parts[1].strip()
                
                if not api_key or api_key == "your_resend_api_key":
                    print(f"❌ RESEND_API_KEY is not configured (empty or placeholder)")
                    return False
                
                if not api_key.startswith("re_"):
                    print(f"❌ RESEND_API_KEY doesn't start with 're_' - may be invalid")
                    print(f"   Current value: {api_key[:20]}...")
                    return False
                
                print(f"✅ RESEND_API_KEY is configured")
                print(f"   Value: {api_key[:10]}...{api_key[-10:]}")
                return True
    
    print("❌ RESEND_API_KEY not properly configured")
    return False

def check_python_config():
    """Check if config.py loads environment variables"""
    print("\n" + "="*60)
    print("STEP 2: Checking Python Configuration")
    print("="*60)
    
    try:
        from config import Config
        
        api_key = getattr(Config, 'RESEND_API_KEY', None)
        from_email = getattr(Config, 'RESEND_FROM_EMAIL', None)
        
        if not api_key:
            print("❌ Config.RESEND_API_KEY is empty")
            return False
        
        print("✅ Config.RESEND_API_KEY is loaded")
        print(f"   Value: {str(api_key)[:10]}...{str(api_key)[-10:]}")
        
        if from_email:
            print(f"✅ Config.RESEND_FROM_EMAIL is set to: {from_email}")
        else:
            print("⚠️  Config.RESEND_FROM_EMAIL is not set (using default)")
        
        return True
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False

def check_email_service():
    """Check if email service functions are available"""
    print("\n" + "="*60)
    print("STEP 3: Checking Email Service Functions")
    print("="*60)
    
    try:
        from utils.email_service import send_offer_letter_email, _dispatch_email
        
        print("✅ email_service.py imports successfully")
        print("   - send_offer_letter_email: Available")
        print("   - _dispatch_email: Available")
        return True
    except Exception as e:
        print(f"❌ Error importing email_service: {e}")
        return False

def check_database():
    """Check if database has documents table"""
    print("\n" + "="*60)
    print("STEP 4: Checking Database Schema")
    print("="*60)
    
    try:
        import sqlite3
        from config import Config
        
        db_path = Config.SQLITE_DB_PATH
        
        if not os.path.exists(db_path):
            print(f"❌ Database not found at: {db_path}")
            return False
        
        print(f"✅ Database exists at: {db_path}")
        
        # Check tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        
        if "documents" not in table_names:
            print("❌ 'documents' table not found in database")
            print(f"   Available tables: {table_names}")
            return False
        
        print("✅ 'documents' table exists")
        
        # Check documents table columns
        cursor.execute("PRAGMA table_info(documents)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        required_cols = ['id', 'application_id', 'email_status', 'email_message_id']
        missing = [col for col in required_cols if col not in column_names]
        
        if missing:
            print(f"⚠️  Missing columns in documents table: {missing}")
        else:
            print(f"✅ All required columns exist in documents table")
        
        # Check applications table
        if "applications" not in table_names:
            print("❌ 'applications' table not found in database")
            return False
        
        print("✅ 'applications' table exists")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def check_resend_api():
    """Test connection to Resend API"""
    print("\n" + "="*60)
    print("STEP 5: Testing Resend API Connection")
    print("="*60)
    
    try:
        import requests
        from config import Config
        
        api_key = Config.RESEND_API_KEY
        
        if not api_key or not api_key.startswith("re_"):
            print("❌ RESEND_API_KEY not properly configured - skipping API test")
            return False
        
        print("ℹ️  Attempting to connect to Resend API...")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Test with a simple API call (no email sent)
        url = "https://api.resend.com/emails"
        
        # Just test the connection (don't actually send)
        try:
            # This will fail without proper payload, but tests connectivity
            response = requests.post(
                url,
                headers=headers,
                json={},  # Empty payload will fail validation
                timeout=5
            )
            
            if response.status_code == 422:
                print("✅ Resend API is reachable and API key is valid!")
                print(f"   (422 is expected for incomplete payload)")
            elif response.status_code == 401:
                print("❌ RESEND_API_KEY is invalid (401 Unauthorized)")
                return False
            else:
                print(f"ℹ️  Resend API responded with status {response.status_code}")
            
            return True
        except Exception as e:
            print(f"⚠️  Could not reach Resend API: {e}")
            print(f"   This is OK if network is unavailable")
            return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_email_sending():
    """Optional: Test actual email sending"""
    print("\n" + "="*60)
    print("STEP 6: Testing Email Sending (Optional)")
    print("="*60)
    
    try:
        from utils.email_service import _dispatch_email
        
        test_email = input("Enter test email address (or press Enter to skip): ").strip()
        
        if not test_email:
            print("⏭️  Skipping email test")
            return True
        
        print(f"\nℹ️  Sending test email to: {test_email}")
        print("   Please wait...\n")
        
        success, result = _dispatch_email(
            to_email=test_email,
            subject="WebIntern Email Test",
            html_content="<h1>Test Email</h1><p>If you received this, email is working!</p>"
        )
        
        if success:
            print("\n✅ Test email sent successfully!")
            print(f"   Message ID: {result.get('id')}")
            print(f"   Check your inbox ({test_email}) for the test email")
            return True
        else:
            print(f"\n❌ Test email failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False

def main():
    """Run all checks"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "   EMAIL CONFIGURATION DIAGNOSTIC TOOL".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {}
    
    results['env'] = check_env_file()
    results['config'] = check_python_config()
    results['service'] = check_email_service()
    results['database'] = check_database()
    results['api'] = check_resend_api()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_passed = all(results.values())
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check.upper()}: {status}")
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✅ All checks passed! Email should be working.")
        print("\nNow test by:")
        print("1. Start Flask: python app.py")
        print("2. Open http://localhost:5000")
        print("3. Create account and apply for internship")
        print("4. Watch terminal for: [✅ EMAIL SENT]")
        print("5. Check your email inbox for offer letter")
    else:
        print("❌ Some checks failed. See details above.")
        print("\nFix the issues and run this script again.")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
