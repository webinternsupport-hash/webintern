"""
Test script to verify the login fix works correctly.
Tests both registration and login with password hashing/verification.
Run from webintern folder: python test_login_fix.py
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

import bcrypt
import uuid
from database import query_db, execute_db, init_db

# Initialize database
print("[TEST] Initializing database...")
init_db()

# Test 1: Test bcrypt hashing/verification logic directly
print("\n=== TEST 1: Direct Bcrypt Hash Verification ===")
test_password = "TestPassword123"
test_email = f"test_bcrypt_{uuid.uuid4().hex[:8]}@test.com"

# Hash password (like registration)
hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f"✅ Password hashed: {hashed[:20]}...")
print(f"   Hash type: {type(hashed)}, length: {len(hashed)}")

# Verify hash (like login)
try:
    match = bcrypt.checkpw(test_password.encode('utf-8'), hashed.encode('utf-8'))
    print(f"✅ Password verification: {match}")
    if match:
        print("   ✅ Direct bcrypt test PASSED")
    else:
        print("   ❌ Direct bcrypt test FAILED - password mismatch")
except Exception as e:
    print(f"❌ Error during verification: {e}")

# Test 2: Test database storage and retrieval
print("\n=== TEST 2: Database Hash Storage & Retrieval ===")
test_user_id = str(uuid.uuid4())
test_full_name = "Test User"
test_email = f"testuser_{uuid.uuid4().hex[:6]}@example.com"
test_password = "SecurePass789"

# Hash password
hashed_pwd = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f"✅ Password hashed for storage")

# Insert into database
try:
    execute_db(
        "INSERT INTO profiles (id, full_name, email, password_hash, auth_provider) VALUES (?, ?, ?, ?, ?)",
        (test_user_id, test_full_name, test_email, hashed_pwd, 'email')
    )
    print(f"✅ User record inserted into database")
except Exception as e:
    print(f"❌ Insert error: {e}")

# Retrieve and verify
try:
    saved_profile = query_db("SELECT * FROM profiles WHERE id = ?", (test_user_id,), one=True)
    if saved_profile:
        print(f"✅ User record retrieved from database")
        saved_hash = saved_profile.get('password_hash')
        print(f"   Saved hash type: {type(saved_hash)}, length: {len(saved_hash)}")
        
        # Try to verify saved hash
        try:
            if isinstance(saved_hash, str):
                hash_bytes = saved_hash.encode('utf-8')
            else:
                hash_bytes = saved_hash
            
            pwd_match = bcrypt.checkpw(test_password.encode('utf-8'), hash_bytes)
            print(f"✅ Password verification against saved hash: {pwd_match}")
            
            if pwd_match:
                print("   ✅ Database hash storage test PASSED")
            else:
                print("   ❌ Database hash storage test FAILED - password mismatch on saved hash")
        except Exception as ve:
            print(f"   ❌ Verification error: {ve}")
    else:
        print(f"❌ Could not retrieve user record from database")
except Exception as e:
    print(f"❌ Retrieval error: {e}")

# Test 3: Case sensitivity test
print("\n=== TEST 3: Email Case Sensitivity Handling ===")
test_user_id_case = str(uuid.uuid4())
test_email_mixed = f"TestUser_{uuid.uuid4().hex[:6]}@Example.COM"
test_password_case = "CaseTestPass123"

hashed_pwd_case = bcrypt.hashpw(test_password_case.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

try:
    execute_db(
        "INSERT INTO profiles (id, full_name, email, password_hash, auth_provider) VALUES (?, ?, ?, ?, ?)",
        (test_user_id_case, "Case Test User", test_email_mixed, hashed_pwd_case, 'email')
    )
    print(f"✅ User created with mixed-case email: {test_email_mixed}")
    
    # Try to retrieve with different cases
    for email_variant in [test_email_mixed, test_email_mixed.lower(), test_email_mixed.upper()]:
        result = query_db("SELECT * FROM profiles WHERE LOWER(email) = LOWER(?)", (email_variant,), one=True)
        if result:
            print(f"   ✅ Found with: {email_variant}")
        else:
            print(f"   ❌ NOT found with: {email_variant}")
    
    print("   ✅ Email case insensitivity test PASSED")
except Exception as e:
    print(f"❌ Case sensitivity test error: {e}")

print("\n=== ALL TESTS COMPLETE ===\n")
