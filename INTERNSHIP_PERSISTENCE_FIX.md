# Internship Persistence Fix - Data Retention After Logout/Login

## Problem Explained

**Issue:** When users logout and login again, their enrolled internships disappear.

**Root Cause:** 
1. User creates account with Google login
2. Applications stored in database with their unique user_id
3. On logout and re-login, a NEW user_id was being generated
4. System couldn't find old applications under new user_id
5. Data appeared "deleted" (but actually just orphaned)

---

## Solution Implemented

### ✅ Fix 1: Email-Based User ID Lookup (CRITICAL)

**File:** `routes/auth_routes.py` - `sync_google_user()` function

**What Changed:**
```python
# OLD (BUG): Generated new UUID each login
user_uuid = google_sub_to_uuid(user_id or email)  # Different each time!

# NEW (FIXED): Lookup by email first
existing_local = query_db("SELECT * FROM profiles WHERE email = ?", (email,), one=True)
if existing_local:
    user_uuid = existing_local['id']  # REUSE same ID
```

**Why This Fixes It:**
- Email is unique and permanent
- Every login with same email = same user_id
- Applications linked to user_id are preserved

---

### ✅ Fix 2: Application Persistence Verification

**File:** `routes/application_routes.py` - `create_application()` function

**What Changed:**
- Added logging to track when applications are created
- Added verification check after saving
- Error handling if save fails
- Console logs for debugging

**Example Log:**
```
[Application Created] ID: abc-123-def, User: user-456, Internship: int-789
[Application Verified] Application saved successfully: abc-123-def
```

---

## How Data is Now Preserved

### User Registration Flow:
```
1. Google Login with email@example.com
   ↓
2. Check if profile exists by EMAIL
   ↓
3. YES - Reuse existing user_id → All old applications accessible
4. NO - Create new user with deterministic UUID based on email
```

### Data Retrieval Flow:
```
1. User logs in
   ↓
2. JWT decoded → Gets user_id from token
   ↓
3. Query: SELECT * FROM applications WHERE user_id = {id}
   ↓
4. Display all internships for this user_id
```

---

## Database Verification

### Check If User Data Is Persisted:

```bash
# Open SQLite database
sqlite3 webintern/webintern.db

# View all users
SELECT id, full_name, email, auth_provider FROM profiles LIMIT 10;

# View all applications
SELECT id, user_id, internship_id, status, start_date FROM applications LIMIT 10;

# Check specific user's applications
SELECT * FROM applications WHERE user_id = 'USER_ID_HERE';

# Exit
.exit
```

### Expected Output:
```
id                                    full_name      email              auth_provider
------------------------------------  ----------     ---------------    -----------
550e8400-e29b-41d4-a716-44665544000  John Doe       john@example.com   google
```

---

## Testing the Fix

### Test Case 1: Register → Enroll → Logout → Login

**Step 1:** Register with Google
- Visit: http://127.0.0.1:5000
- Click "Sign In with Google"
- Complete profile (college, department, phone)
- Remember the email used

**Step 2:** Enroll in internship
- Click "Explore Internships"
- Select any internship
- Click "Apply Now"
- Check email for offer letter

**Step 3:** Verify enrollment saved
- Open browser DevTools (F12)
- Go to Application tab → Local Storage
- Note the `user_id` in token

**Step 4:** Logout
- Click profile menu → Logout
- Clear cookies/cache if needed

**Step 5:** Login again with SAME email
- Click "Sign In with Google"
- Use the SAME Google account
- Go to dashboard
- ✅ **INTERNSHIP SHOULD STILL BE THERE**

---

### Test Case 2: Database Direct Verification

```bash
# After registering user and enrolling in internship:

# Check user ID
sqlite3 webintern/webintern.db "SELECT id, email FROM profiles WHERE email = 'test@example.com';"
# Returns: 550e8400-e29b-41d4-a716-44665544000 | test@example.com

# Check applications for that user
sqlite3 webintern/webintern.db "SELECT id, user_id, internship_id, status FROM applications WHERE user_id = '550e8400-e29b-41d4-a716-44665544000';"
# Returns: application record with that user_id

# Logout and login again - same user_id should be reused
sqlite3 webintern/webintern.db "SELECT id, email, auth_provider FROM profiles WHERE email = 'test@example.com';"
# Should return SAME ID (not a new one)
```

---

## API Verification

### Test Endpoint: GET /api/applications/me

**Before Fix (Bug):**
```
Login 1st time → GET /api/applications/me → Returns applications ✅
Logout → Logout  
Login 2nd time → GET /api/applications/me → Returns EMPTY ❌
```

**After Fix:**
```
Login 1st time → GET /api/applications/me → Returns applications ✅
Logout → Logout  
Login 2nd time → GET /api/applications/me → Returns SAME applications ✅
```

**Test in browser console:**
```javascript
// After login
fetch('/api/applications/me', {
  headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
})
.then(r => r.json())
.then(data => console.log(data.applications.length))

// After logout → login again
// Should print SAME number of applications
```

---

## Console Logs for Debugging

When creating application, check browser console:

```
[Application Created] ID: app-123, User: user-456, Internship: int-789
[Application Verified] Application saved successfully: app-123
```

If you see these logs, application was successfully saved.

---

## Server Logs

Start backend and watch console:

```bash
python webintern/app.py
```

When creating application, you should see:
```
[Application Created] ID: abc-def-ghi, User: 550e8400-e29b-41d4, Internship: xyz-789
[Application Verified] Application saved successfully: abc-def-ghi
```

---

## Troubleshooting

### Problem: Still Losing Applications on Logout/Login

**Check 1:** Email consistency
```javascript
// After login, check what email is being used
console.log(localStorage.getItem('user_profile'))
// Note the email
```

**Check 2:** User ID consistency
```bash
# Query database
sqlite3 webintern/webintern.db "SELECT id, email FROM profiles WHERE email = 'YOUR_EMAIL';"
# Should always return SAME id for same email
```

**Check 3:** Application exists
```bash
# Query database
sqlite3 webintern/webintern.db "SELECT id FROM applications WHERE user_id = 'THE_ID_FROM_ABOVE';"
# Should show applications created
```

---

## What Was NOT Changed

✅ No database schema changes  
✅ No API endpoints deleted  
✅ No breaking changes  
✅ No frontend logic changes  

**Only changed:** How user_id is determined during Google login (email-based lookup instead of Google ID)

---

## Summary

| Before | After |
|--------|-------|
| User ID changes on each Google login | User ID consistent (based on email) |
| Applications orphaned | Applications preserved |
| Data loss on logout/login | Data persists |
| Different user created each time | Same user detected |

The fix ensures **email is the primary user identifier**, making data persistent across logins regardless of Google account state changes.
