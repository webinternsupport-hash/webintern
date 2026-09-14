# QUICK TEST GUIDE - 5 Minutes to Verify All Fixes

Run these tests immediately after deployment to confirm everything works.

---

## TEST 1: Old Account Shows Enrollments (30 seconds)

**Setup:**
- Use existing account or create one and apply to internship, then logout

**Test:**
1. Login with email
2. Dashboard loads
3. You see "My Internships" section populated ✅
4. At least one enrollment card visible ✅

**Expected:** Enrollment card shows internship title, dates, progress bar

**If FAIL:**
- Backend logs: `grep "/api/applications/me" app.log`
- Check database: `sqlite3 webintern.db "SELECT * FROM applications LIMIT 1;"`

---

## TEST 2: Data Persists After Logout (1 minute)

**Test:**
1. While logged in, note your enrollments
2. Click Logout
3. Login again
4. Same enrollments still visible ✅
5. Refresh page
6. Data still there ✅

**Expected:** Data appears immediately (from IndexedDB cache) and stays after refresh

**If FAIL:**
- Open DevTools → Storage → IndexedDB → InternshipComLocalDB
- Check if `enrollments` object store has data
- If empty: IndexedDB not syncing

---

## TEST 3: Offer Letter Email Sends (2 minutes)

**Setup:**
- Have a fresh email account ready to receive test email

**Test:**
1. Login
2. Apply to a new internship
3. See "Application submitted" message (HTTP 201) ✅
4. Check backend logs for: `[✅ Email Success]` or `[Email Thread Started]` ✅
5. Wait 30 seconds
6. Check email inbox
7. Email received with subject "Your WebIntern Internship Offer Letter" ✅
8. Email has PDF attachment ✅

**Expected:** Email arrives within 30 seconds with PDF attached

**If FAIL - Email Not Received:**
```bash
# Check logs
grep "Email Thread" app.log | tail -5

# If you see: [❌ EMAIL BLOCKED] RESEND API KEY NOT CONFIGURED
# → Fix: Update .env with real RESEND_API_KEY=re_xxx

# If you see: [❌ Email Failed] with error
# → Check RESEND_API_KEY format and database status
```

---

## TEST 4: PDF Download Works (1 minute)

**Test:**
1. Dashboard → Find an enrollment
2. Click "Download" button
3. Browser downloads file named `Offer_Letter_XXXXX.pdf` ✅
4. File is readable PDF (open to verify) ✅

**Expected:** File downloads immediately (if cached) or within 2-3 seconds (if regenerating)

**If FAIL - Download Doesn't Work:**
```bash
# Check file exists
ls -la storage/generated/offers/offer_*.pdf

# Check permissions
chmod 755 storage/generated/offers/

# Test via curl
curl -v http://localhost:5000/api/applications/{APP_ID}/offer-letter.pdf
```

---

## TEST 5: View Offer Letter in Browser (30 seconds)

**Test:**
1. Dashboard → Find enrollment
2. Click "View" button
3. PDF opens in new browser tab ✅
4. PDF is readable and shows offer letter content ✅
5. Close tab

**Expected:** PDF displays inline in browser within 1 second

**If FAIL:**
- Check file path: `storage/generated/offers/offer_{id}.pdf` exists
- Check response headers: `Content-Type: application/pdf`

---

## TEST 6: Token Lasts 7 Days (Manual Check)

**Test:**
1. Login
2. Open browser DevTools → Application → Storage → Cookies
3. Find `access_token` (or check localStorage)
4. Decode token at https://jwt.io/
5. In payload, find `exp` field
6. Calculate seconds: `(exp - now) / 86400` = days
7. Should be ~6.99 days ✅

**Expected:** Token shows expiration in 7 days

**Alternative - Via Backend:**
```python
import jwt
import time
token = "your_access_token"
decoded = jwt.decode(token, options={"verify_signature": False})
exp_time = decoded['exp']
now = int(time.time())
days_remaining = (exp_time - now) / 86400
print(f"Token expires in {days_remaining:.1f} days")  # Should be ~7
```

---

## TEST 7: Complete User Journey (Instagram Model) (3 minutes)

**Full Journey:**
1. **Signup** → Create account with email
2. **Profile** → Add college, degree, department
3. **Browse** → Go to internships page
4. **Apply** → Apply to 2-3 internships
5. **Dashboard** → See all enrollments
6. **Download** → Download one offer letter
7. **Logout** → Click logout
8. **Login** → Log back in
9. **Verify** → All enrollments still visible ✅
10. **Refresh** → Hard refresh (Ctrl+F5)
11. **Check** → Enrollments still there ✅
12. **Email** → Check inbox for all offer letters ✅

**Expected:**
- Instant dashboard load on login
- All data persists across sessions
- All emails received within 5 minutes

---

## Debug Commands

### Check Email Status
```bash
# See all email sends
grep "Email" app.log | tail -20

# See only failures
grep "Email.*FAILED\|Email.*ERROR" app.log

# See Resend API details
grep "dispatch_email\|RESEND\|_get_resend_key" app.log
```

### Check Database
```bash
# Count applications
sqlite3 webintern.db "SELECT COUNT(*) FROM applications;"

# Check latest enrollment
sqlite3 webintern.db "SELECT id, user_id, internship_id, status FROM applications ORDER BY applied_at DESC LIMIT 1;"

# Check offer letters
sqlite3 webintern.db "SELECT COUNT(*) FROM documents WHERE document_type='OFFER_LETTER';"

# Check email status
sqlite3 webintern.db "SELECT document_number, email_status FROM documents LIMIT 10;"
```

### Check File Storage
```bash
# List cached PDFs
ls -lah storage/generated/offers/

# Count cached PDFs
find storage/generated/offers -name "*.pdf" | wc -l

# Check permissions
stat storage/generated/offers/
```

### Check Frontend Storage
```javascript
// Open DevTools Console and run:

// Check IndexedDB
(async () => {
  const db = await new Promise(r => {
    const req = indexedDB.open('InternshipComLocalDB');
    req.onsuccess = () => r(req.result);
  });
  const tx = db.transaction('enrollments', 'readonly');
  const store = tx.objectStore('enrollments');
  const all = await new Promise(r => {
    const req = store.getAll();
    req.onsuccess = () => r(req.result);
  });
  console.log('IndexedDB Enrollments:', all);
})();

// Check localStorage
console.log('Access Token:', localStorage.getItem('access_token'));
console.log('User Profile:', localStorage.getItem('user_profile'));

// Check cookies
console.log('Cookies:', document.cookie);
```

---

## Common Issues & Fixes

| Issue | Check | Fix |
|-------|-------|-----|
| Dashboard empty | `/api/applications/me` returns empty array | Verify applications in DB |
| Email not sent | Logs show `[❌ EMAIL BLOCKED]` | Add RESEND_API_KEY to .env |
| PDF download fails | Directory doesn't exist | Run: `mkdir -p storage/generated/offers/` |
| Token expires in 1 day | Check JWT_EXPIRATION_HOURS | Update config.py to 168 hours |
| Data lost on logout | IndexedDB not syncing | Refresh page to re-sync from server |

---

## Success Checklist

- [ ] Test 1: Old account shows enrollments ✅
- [ ] Test 2: Data persists after logout/login ✅
- [ ] Test 3: Offer letter email sent ✅
- [ ] Test 4: PDF download works ✅
- [ ] Test 5: PDF view in browser works ✅
- [ ] Test 6: Token configured for 7 days ✅
- [ ] Test 7: Complete journey works like Instagram ✅

**If ALL ✅:** System ready for production!

**If any ❌:** Debug using commands above and check logs

---

## Run Automated Tests

```bash
# Run comprehensive test suite
python test_comprehensive_fixes.py

# Expected output: 7/7 tests passed

# If any fail:
# 1. Read the failure message
# 2. Run appropriate debug command above
# 3. Fix configuration/permissions
# 4. Re-run tests
```

---

**Time to Run:** ~5 minutes  
**Effort:** Minimal (mostly clicking buttons + waiting for email)  
**Value:** Confirms all 5 critical issues are fixed  
**Confidence:** 100% ready if all pass
