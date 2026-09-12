# IndexedDB Persistence - Test Execution Plan

## Pre-Test Setup
1. Clear browser cache and storage (Ctrl+Shift+Delete or Settings > Clear browsing data)
2. Open browser DevTools (F12)
3. Go to Application tab → Storage → IndexedDB
4. Navigate to application at `http://localhost:5000`

---

## Test Suite 1: Account Creation & Persistence

### Test 1.1: Create New Account
**Steps**:
1. Click "Get Started" or go to #/register
2. Fill form:
   - Full Name: `John Doe`
   - Email: `john.test@example.com`
   - Phone: `9876543210`
   - College: `Anna University`
   - Department: `Computer Science`
   - Password: `Password123`
3. Click "Create Account"

**Expected Results**:
- ✅ Account created successfully
- ✅ Redirected to #/dashboard
- ✅ User profile visible with name "John Doe"
- ✅ In DevTools → IndexedDB → InternshipComLocalDB → users store, see record with userId
- ✅ Email, name, college, department are stored

**Verification**:
```javascript
// Open DevTools Console, run:
const db = await new Promise(resolve => {
  const req = indexedDB.open('InternshipComLocalDB', 1);
  req.onsuccess = () => resolve(req.result);
});
const tx = db.transaction('users', 'readonly');
const store = tx.objectStore('users');
const allUsers = await new Promise(resolve => {
  const req = store.getAll();
  req.onsuccess = () => resolve(req.result);
});
console.log('Stored users:', allUsers);
```

---

## Test Suite 2: Logout & Login Persistence

### Test 2.1: Logout Then Login
**Steps**:
1. From dashboard, click "Sign Out"
2. Verify redirected to home page
3. Go to #/login
4. Enter credentials: `john.test@example.com` / `Password123`
5. Click "Sign In"

**Expected Results**:
- ✅ Logout successful (tokens cleared from localStorage)
- ✅ Login successful
- ✅ Redirected to dashboard
- ✅ User profile still shows "John Doe"
- ✅ In DevTools, same user record still in IndexedDB

**Key Assertion**:
- Session tokens are cleared (localStorage empty)
- But user profile data persists in IndexedDB
- Account is restored on login

---

## Test Suite 3: Enrollment Persistence

### Test 3.1: Enroll in Internship
**Steps**:
1. From dashboard, click #/internships
2. Click on any internship card (e.g., "Software Development Internship")
3. Read details, click "Apply Now"
4. Verify enrollment created

**Expected Results**:
- ✅ Application submitted
- ✅ Redirected to #/dashboard
- ✅ Internship appears in "My Internships" tab
- ✅ In DevTools → IndexedDB → enrollments store, see enrollment record
- ✅ Record has correct userId, internshipId, internshipTitle

### Test 3.2: Refresh Page - Enrollment Still Visible
**Steps**:
1. From dashboard with enrollment visible
2. Press F5 to refresh page
3. Verify enrollment still visible

**Expected Results**:
- ✅ Dashboard reloads
- ✅ Enrollment is immediately visible (from IndexedDB)
- ✅ No "Loading..." state needed (IndexedDB is instant)

### Test 3.3: Logout → Login → Enrollment Restored
**Steps**:
1. From dashboard with enrollment visible
2. Click "Sign Out"
3. Click #/login, enter credentials
4. Verify enrollment restored

**Expected Results**:
- ✅ Enrollment still visible on dashboard
- ✅ Persistent data survived logout/login cycle

### Test 3.4: Close & Reopen Browser - Enrollment Persists
**Steps**:
1. From dashboard with enrollment visible
2. Close browser completely (not just tab)
3. Reopen browser
4. Navigate to application
5. Go to #/login and login
6. Verify enrollment restored

**Expected Results**:
- ✅ Enrollment still visible on dashboard
- ✅ Persistent data survived browser restart

---

## Test Suite 4: Multiple Enrollments

### Test 4.1: Enroll in Multiple Internships
**Steps**:
1. From dashboard, go to #/internships
2. Enroll in Internship A
3. Go back to #/internships
4. Enroll in Internship B
5. Go back to #/internships
6. Enroll in Internship C
3. Return to #/dashboard → "My Internships"

**Expected Results**:
- ✅ All three internships visible
- ✅ In IndexedDB, three enrollment records with same userId
- ✅ All enrollments scoped to same user

**Verification**:
```javascript
// In DevTools Console:
const db = await new Promise(resolve => {
  const req = indexedDB.open('InternshipComLocalDB', 1);
  req.onsuccess = () => resolve(req.result);
});
const tx = db.transaction('enrollments', 'readonly');
const index = tx.objectStore('enrollments').index('userId');
const userId = JSON.parse(localStorage.getItem('user_profile')).id;
const enrollments = await new Promise(resolve => {
  const req = index.getAll(userId);
  req.onsuccess = () => resolve(req.result);
});
console.log('Enrollments for user:', enrollments);
// Should show 3 records
```

---

## Test Suite 5: Offer Letter Persistence

### Test 5.1: Offer Letter is Saved
**Steps**:
1. Enroll in an internship (automatically generates offer letter)
2. From dashboard, click "📄 Offer" button

**Expected Results**:
- ✅ Offer letter downloads or opens in new tab
- ✅ In IndexedDB → offerLetters store, see record with correct internshipTitle

### Test 5.2: Offer Letter Survives Logout/Login
**Steps**:
1. Enroll in internship (have offer letter saved)
2. Logout and login again
3. Go to #/dashboard Documents tab
4. Try to view/download offer letter

**Expected Results**:
- ✅ Offer letter still accessible
- ✅ Same document data is displayed

---

## Test Suite 6: Cross-Account Isolation

### Test 6.1: Create Second Account
**Steps**:
1. Logout from Account A
2. Go to #/register
3. Create new account:
   - Full Name: `Jane Smith`
   - Email: `jane.test@example.com`
   - Phone: `9876543211`
   - College: `IIT Bombay`
   - Department: `Mechanical Engineering`
   - Password: `Password123`

**Expected Results**:
- ✅ New account created
- ✅ In IndexedDB → users store, see TWO user records (one for John, one for Jane)
- ✅ Different userIds

### Test 6.2: Enroll Account B in Different Internship
**Steps**:
1. From Account B (Jane) dashboard
2. Go to #/internships
3. Enroll in a DIFFERENT internship (e.g., Marketing Internship)
4. Return to dashboard

**Expected Results**:
- ✅ Only THIS internship is visible (not John's enrollment)
- ✅ In IndexedDB → enrollments store, see enrollments with DIFFERENT userId
- ✅ Enrollments are properly scoped

### Test 6.3: Switch Back to Account A - No Leakage
**Steps**:
1. Logout from Account B
2. Login as Account A (John)
3. Go to #/dashboard

**Expected Results**:
- ✅ Only John's enrollments visible
- ✅ Jane's enrollments NOT visible
- ✅ No cross-account data leakage

**Verification in DevTools**:
```javascript
// Check that only current user's data is displayed
const user = JSON.parse(localStorage.getItem('user_profile'));
console.log('Current user:', user.email);

// In Console, verify enrollments belong to this user only
// Should see enrollments matching current userId only
```

---

## Test Suite 7: Prevent Duplicate Enrollments

### Test 7.1: Cannot Enroll Twice in Same Internship
**Steps**:
1. Login as Account A
2. Enroll in "Software Development Internship"
3. Go back to internship detail page
4. Try to apply again

**Expected Results**:
- ✅ Either prevented from applying again, or creates only one enrollment
- ✅ In IndexedDB → enrollments, no duplicate with same (userId, internshipId)

---

## Test Suite 8: Profile Data Persistence

### Test 8.1: Profile Information Saved
**Steps**:
1. After login, profile section might be available
2. Verify name, email, college, department display correctly

**Expected Results**:
- ✅ User profile information displayed from IndexedDB
- ✅ Data matches what was stored during registration

---

## Test Suite 9: Activity & Progress Tracking

### Test 9.1: Activity is Tracked
**Steps**:
1. Complete some internship tasks/activities
2. Verify activity appears in activity log (if implemented)

**Expected Results**:
- ✅ Activities saved to IndexedDB → activities store
- ✅ Scoped to correct userId
- ✅ Survives logout/login

---

## Test Suite 10: Offline Access

### Test 10.1: Offline Viewing
**Steps**:
1. Login and enroll in internship
2. Disconnect internet (unplug ethernet or disable WiFi)
3. Refresh page or navigate dashboard

**Expected Results**:
- ✅ Dashboard still loads (from IndexedDB)
- ✅ Enrollments still visible
- ✅ No network errors preventing view

### Test 10.2: Sync on Reconnect
**Steps**:
1. Reconnect internet
2. Refresh page

**Expected Results**:
- ✅ Fresh data fetched from server
- ✅ IndexedDB updated with latest data
- ✅ User experience seamless

---

## Test Suite 11: Android PWA Installation

### Test 11.1: Install PWA
**Steps**:
1. On Android phone, open application
2. Press menu (usually 3 dots)
3. Click "Install app" or "Add to Home Screen"
4. Wait for installation to complete

**Expected Results**:
- ✅ App installed as PWA
- ✅ Can launch from home screen

### Test 11.2: PWA Login & Enrollment
**Steps**:
1. Open PWA
2. Login with credentials
3. Enroll in internship
4. Close app completely
5. Reopen app from home screen

**Expected Results**:
- ✅ Still logged in (if session not expired)
- ✅ Enrollment still visible
- ✅ IndexedDB data persisted

### Test 11.3: PWA Offline
**Steps**:
1. In PWA, enable airplane mode
2. Navigate dashboard
3. Try viewing enrollments

**Expected Results**:
- ✅ Data still visible from IndexedDB
- ✅ App provides offline-first experience

---

## Test Suite 12: Edge Cases

### Test 12.1: Multiple Tabs/Windows
**Steps**:
1. Open application in Tab 1
2. Login in Tab 1
3. Open application in Tab 2 (same browser)
4. Both tabs should see same user

**Expected Results**:
- ✅ Both tabs show same user data
- ✅ IndexedDB transaction is shared

### Test 12.2: Private/Incognito Mode
**Steps**:
1. Open in Private/Incognito mode
2. Register new account
3. Go to #/dashboard
4. Close Private window
5. Reopen Private window

**Expected Results**:
- ✅ Data persists within Private session
- ✅ NOT shared with normal mode
- ✅ Separate IndexedDB instance

### Test 12.3: Large Data Sets
**Steps**:
1. Enroll in 20+ internships
2. Verify all visible
3. Check performance

**Expected Results**:
- ✅ Dashboard still responsive
- ✅ No performance degradation
- ✅ All enrollments loaded correctly

---

## Manual Verification Checklist

### Storage Layer
- [ ] `storage.js` loads without errors
- [ ] `Storage.init()` completes successfully
- [ ] IndexedDB database created with correct name and version
- [ ] All object stores created (users, enrollments, offerLetters, etc.)
- [ ] Indexes created correctly

### Account Scoping
- [ ] Every record has `userId` field
- [ ] Read operations filter by `userId`
- [ ] Cross-account data not visible
- [ ] userId is consistent across sessions

### Logout Behavior
- [ ] `localStorage.getItem('access_token')` returns null after logout
- [ ] `localStorage.getItem('user_profile')` returns null after logout
- [ ] IndexedDB data NOT cleared on logout
- [ ] Toast shows "logged out successfully"

### Login Restoration
- [ ] After login, `Storage.restoreUserAccount()` called
- [ ] Previous enrollments immediately visible
- [ ] No duplicate enrollments created
- [ ] Profile data matches what was stored

### Persistence
- [ ] Page refresh: data persists
- [ ] Browser restart: data persists
- [ ] Logout/login: data persists
- [ ] Offline viewing: data visible

---

## Performance Metrics

Monitor these in DevTools:
- IndexedDB read time: < 50ms per query
- Dashboard load time with 10 enrollments: < 2s
- Memory usage: < 5MB for typical user data
- Storage usage: < 1MB per user account

---

## Failure Scenarios

### If IndexedDB Fails
- ✅ App continues working with server data only
- ✅ No data loss
- ✅ Error logged to console
- ✅ User not blocked

### If userId Not Found
- ✅ Graceful degradation
- ✅ Server data still fetched
- ✅ No error pages

### If Quota Exceeded
- ✅ Log warning to console
- ✅ App continues functioning
- ✅ Oldest data might be cleared

---

## Sign-Off Criteria

All tests PASS when:
1. ✅ User data persists after logout/login
2. ✅ Enrollments visible after page refresh
3. ✅ Cross-account data properly isolated
4. ✅ No duplicate enrollments
5. ✅ Offline access works
6. ✅ Android PWA installs and persists data
7. ✅ No console errors
8. ✅ Performance acceptable
9. ✅ IndexedDB stores visible in DevTools
10. ✅ userId properly scopes all records

---

## Test Execution Record

Use this to track test runs:

| Test ID | Description | Status | Notes | Date |
|---------|-------------|--------|-------|------|
| 1.1 | Create new account | PASS/FAIL | | |
| 2.1 | Logout then login | PASS/FAIL | | |
| 3.1 | Enroll in internship | PASS/FAIL | | |
| 3.2 | Refresh page | PASS/FAIL | | |
| 3.3 | Logout → login → enrollment | PASS/FAIL | | |
| 3.4 | Close → reopen browser | PASS/FAIL | | |
| 4.1 | Multiple enrollments | PASS/FAIL | | |
| 5.1 | Offer letter saved | PASS/FAIL | | |
| 5.2 | Offer letter survives logout/login | PASS/FAIL | | |
| 6.1 | Create second account | PASS/FAIL | | |
| 6.2 | Account B enroll different internship | PASS/FAIL | | |
| 6.3 | Switch back to account A | PASS/FAIL | | |
| 7.1 | Prevent duplicate enrollment | PASS/FAIL | | |
| 10.1 | Offline viewing | PASS/FAIL | | |
| 11.1 | Install PWA | PASS/FAIL | | |
| 11.2 | PWA login & enrollment | PASS/FAIL | | |

