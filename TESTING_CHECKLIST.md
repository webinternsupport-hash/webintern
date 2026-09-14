# 🧪 Testing Checklist - Critical Issues Fixes

## Quick Test (5 Minutes)

### Issue #1: Data Persistence
- [ ] Create new account: `test@webintern.in` / `password123`
- [ ] Enroll in one internship from dashboard
- [ ] **Reload page** (Ctrl+R or Cmd+R)
- [ ] ✅ Verify enrollment is still visible
- [ ] ✅ Verify status hasn't reset to pending

### Issue #2: Login After Registration
- [ ] From the account created above, **log out**
- [ ] Click "Sign In"
- [ ] Enter: `test@webintern.in` / `password123`
- [ ] ✅ Login should succeed
- [ ] ✅ Dashboard should show the same enrollment
- [ ] ✅ No error message about invalid credentials

### Issue #3: Mobile Checkboxes
- [ ] Open DevTools (F12)
- [ ] Set viewport to mobile (375x667 - iPhone SE)
- [ ] Go to signup page (#/register)
- [ ] **Try to tap/click** "I agree to Terms & Conditions" checkbox
- [ ] ✅ Checkbox should visibly toggle (checked/unchecked)
- [ ] ✅ Try clicking the text label - should also toggle checkbox
- [ ] ✅ Checkbox should show checkmark when checked

### Issue #4: Post-Deployment Buttons
**Deployment Site**: https://your-deployment-url

- [ ] Go to dashboard
- [ ] Find "Offer" button on any internship card
- [ ] **Click Offer button**
- [ ] ✅ PDF should download or open in new tab
- [ ] ✅ Browser console should show NO red error messages
- [ ] ✅ Network tab should show API call with status 200
- [ ] **Click Cert button** (if available)
- [ ] ✅ Should show payment modal or certificate PDF
- [ ] **Click Tasks button**
- [ ] ✅ Should open task workspace

### Issue #5: Mobile Profile Display
- [ ] DevTools: Set to mobile (375x667)
- [ ] In bottom nav, tap **Profile icon** (or #/dashboard)
- [ ] Dashboard should show enrolled internships
- [ ] ✅ Internship cards should stack vertically (not in grid)
- [ ] ✅ All text should be readable (no horizontal scroll)
- [ ] ✅ Buttons should be full-width
- [ ] ✅ No content should be hidden behind bottom nav

---

## Medium Test (10 Minutes)

### Complete User Journey
1. **Register & Setup**
   - [ ] Create new account with full details
   - [ ] College: "Test University"
   - [ ] Department: "Computer Science"
   - [ ] Verify all fields save

2. **Enrollment & Persistence**
   - [ ] Enroll in 2 different internships
   - [ ] Wait 2 seconds for data to sync
   - [ ] **Hard refresh page** (Ctrl+Shift+R)
   - [ ] ✅ Both enrollments should still be visible
   - [ ] ✅ Check Network tab: API call to `/api/applications/me` shows data

3. **Task Submission**
   - [ ] Open one internship → Tasks
   - [ ] Try to upload a PDF for week 1
   - [ ] ✅ Upload should complete without errors
   - [ ] **Reload page**
   - [ ] ✅ Uploaded file should still be there

4. **Payment & Certificate** (if configured)
   - [ ] Click "Get Certificate" button
   - [ ] ✅ Should show payment modal or processing screen
   - [ ] ✅ No CORS errors in console

5. **Session Management**
   - [ ] **Log out** (from menu)
   - [ ] ✅ Should go to home page
   - [ ] ✅ Dashboard should not be accessible (redirects to login)
   - [ ] **Log in again** with same email/password
   - [ ] ✅ All enrollments and uploaded tasks should still be there

6. **Mobile Responsiveness**
   - [ ] DevTools: Resize to 375px width
   - [ ] ✅ No horizontal scrolling
   - [ ] ✅ Bottom nav stays visible and usable
   - [ ] ✅ Forms are readable
   - [ ] ✅ All buttons are tappable (min 44px height)

---

## Comprehensive Test (20 Minutes)

### Full Production Validation

#### Part A: Data Persistence (5 min)
```
1. Register as: alice@example.com / Pass@123456
2. Enroll in: Web Development Internship
3. Make Payment (if available)
4. Upload Task PDF
5. Close browser completely
6. Open browser again
7. Visit website (should be on home)
8. Log in with same credentials
9. Verify: Enrollment shows, Payment status shows, Task shows
```

#### Part B: Mobile Experience (5 min)
```
1. DevTools: Mobile (iPhone 12 - 390x844)
2. Go through entire signup flow
3. Test each form field (min 44px height)
4. Test T&C checkbox tapping
5. Test form submission
6. View dashboard in mobile view
7. Test all buttons (full-width, tappable)
8. Scroll through entire page (no horizontal scroll)
```

#### Part C: API Endpoints (5 min)
**On Live/Deployment Site**
```
1. DevTools: Network tab
2. Clear network history
3. Click: Offer Letter button
   - Watch network tab
   - Should see: /api/applications/[id]/offer-letter.pdf
   - Status: 200
   - Type: PDF or application/pdf
4. Click: Certificate button
   - Watch network tab
   - Should see: /api/certificates/[id]/pdf or payment endpoint
   - Status: 200 or 302 (redirect)
5. Click: Tasks button
   - Watch network tab
   - Should see: /api/applications/[id] or similar
   - Status: 200
   - Response: JSON with task data
```

#### Part D: Error Handling (5 min)
```
1. Test wrong password → Error message shown
2. Test non-existent email → Error message shown
3. Uncheck T&C → Can't submit form
4. Network offline → Error message or fallback shown
5. Missing environment variables → Graceful fallback
```

---

## Deployment Checklist

### Before Going Live
- [ ] All code changes committed to git
- [ ] No console errors when running locally
- [ ] Database file exists (webintern.db)
- [ ] Environment variables in .env are set
- [ ] CORS is enabled in app.py
- [ ] All 3 modified files are included in deployment

### After Deployment
- [ ] Website loads without 500 errors
- [ ] Signup page is accessible
- [ ] Can create account successfully
- [ ] Can log in with credentials
- [ ] Dashboard shows data
- [ ] Buttons work and don't show CORS errors
- [ ] Mobile view works (test on real phone)
- [ ] API calls show full URLs in Network tab (not relative paths)

---

## Browser Console Check

Open DevTools (F12) and check **Console** tab for these should NOT appear:

### ❌ These errors mean something is broken:
```
❌ CORS error: Access-Control-Allow-Origin
❌ 404 Not Found: /api/applications/me
❌ Uncaught SyntaxError
❌ TypeError: Cannot read property
❌ Failed to fetch
```

### ✅ These are normal and OK:
```
✅ [Dashboard] Fetching applications from /api/applications/me
✅ [Dashboard] Loaded persisted enrollments: 2
✅ [Storage] Initialized successfully
✅ Any console.warn messages
```

---

## Network Tab Check

In DevTools **Network** tab, look for API calls:

### ✅ Good Requests:
```
URL: https://your-site.com/api/applications/me
Method: GET
Status: 200 OK
Response: { applications: [...] }
```

### ❌ Bad Requests:
```
URL: /api/applications/me (MISSING DOMAIN!)
Method: GET
Status: 404 or CORS error
Response: error or CORS policy violation
```

---

## Mobile Testing on Real Device

### iOS
1. Connect to same WiFi as desktop
2. Open Safari
3. Go to: `http://[YOUR_IP]:5000` (development)
4. Or deployment URL for production
5. Test signup, login, dashboard, buttons

### Android
1. Connect to same WiFi as desktop
2. Open Chrome
3. Go to: `http://[YOUR_IP]:5000`
4. Test all flows
5. DevTools: Tap ⋮ → More Tools → Remote devices to debug

---

## Regression Testing

Make sure you didn't break existing features:

- [ ] Home page loads
- [ ] Explore page shows internships
- [ ] Can search/filter internships
- [ ] Internship detail page works
- [ ] About page loads
- [ ] Contact form works
- [ ] Footer links work
- [ ] Mobile nav opens/closes
- [ ] Bottom nav navigation works

---

## Performance Check

### Load Time
- [ ] Homepage loads in < 3 seconds
- [ ] Dashboard loads in < 2 seconds
- [ ] Buttons respond in < 1 second

### Console
- [ ] No more than 5 console warnings
- [ ] No errors in Network tab
- [ ] No CORS warnings

---

## Sign-Off

**Date Tested**: _______________
**Tester Name**: _______________
**Environment**: ☐ Local ☐ Staging ☐ Production
**Result**: ☐ PASS ☐ FAIL (describe issues below)

```
Issues Found (if any):




```

**Approved for Deploy**: _______________

---

## Quick Commands for Testing

```bash
# Start local development server
python app.py

# Access website locally
http://localhost:5000

# Check database
sqlite3 webintern.db
> SELECT COUNT(*) FROM profiles;
> SELECT COUNT(*) FROM applications;

# Monitor logs
tail -f output.log
```

---

## Contact Support

If tests fail:
1. Check `/webintern/FIXES_IMPLEMENTATION_SUMMARY.md` for details
2. Review console errors (F12 → Console)
3. Check Network tab for API calls
4. Ensure all 3 files are modified
5. Verify database exists
6. Check environment variables are set
