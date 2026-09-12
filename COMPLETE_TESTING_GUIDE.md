# Complete Platform Testing Guide

## 🧪 TEST CHECKLIST

### Phase 1: Login & Authentication

#### Step 1: Clear Browser Cache
```
1. Open DevTools (F12)
2. Go to Application tab
3. Clear localStorage
4. Clear cookies
5. Refresh page (Ctrl+F5)
```

#### Step 2: Login Fresh
```
1. Open http://localhost:5000
2. Click "Get Started" or "Sign In"
3. Enter email and OTP
4. Complete profile (name, phone, college, department)
5. Click "Submit"
6. Should see: "Profile completed successfully!"
```

#### Step 3: Verify Authentication
```
1. Open DevTools (F12)
2. Go to Console tab
3. Type: localStorage.getItem('access_token')
4. Result: Should show a long JWT token (starts with "ey...")
5. If empty: Authentication failed - re-login
```

---

### Phase 2: Browse & Enroll in Internship

#### Step 4: Browse Internships
```
1. Click "Explore" tab (bottom navigation)
2. Wait for internships to load
3. Search box should appear
4. Try searching: "Python" or "React" or "C"
5. Result: Should see matching internships
```

#### Step 5: CRITICAL - Apply for Internship
```
1. Click any internship card (e.g., "Python Backend Development")
2. Click "Apply Now" button
3. Expected: "Submitting application & issuing offer letter..." message
4. Expected: Application created successfully
5. Expected: Redirected to profile with application visible

IF YOU SEE ERROR "Invalid or expired token":
   ⚠️  Token issue - follow solution below
```

**SOLUTION FOR "Invalid or expired token" ERROR:**

```javascript
// In DevTools Console, run:
// 1. Clear token
localStorage.removeItem('access_token');
localStorage.removeItem('user_profile');

// 2. Force page refresh
location.reload();

// 3. Login again with fresh credentials
// 4. Try enrollment again
```

---

### Phase 3: Profile & Progress Tracking

#### Step 6: View Your Applications
```
1. Click "Profile" tab (bottom navigation)
2. Should see welcome banner: "Welcome back! 👋"
3. Should see "My Internships" tab
4. Should show: Enrolled internship with progress bar
5. Click "Open Task Workspace & Submit Assignments"
6. Should see: 4 weeks of tasks
```

#### Step 7: Task Submission
```
1. In workspace, find "Week 1" task
2. Click "Upload" button
3. Select any PDF file
4. Click "Upload & Submit PDF"
5. Result: "Assignment PDF uploaded successfully!"
6. Refresh page: Should show task marked as "submitted"
```

---

### Phase 4: Certificate & Payment

#### Step 8: View Certificate Option
```
1. Back on Profile page
2. In application card, click "🏆 Certificate" button
3. Expected: "Certificate" modal opens
4. Shows: Certificate payment option (₹199)
5. Shows: Button "💳 Pay ₹199 Certificate Fee"
```

#### Step 9: Razorpay Payment TEST
```
Click "💳 Pay ₹199 Certificate Fee"
Expected: Razorpay checkout opens

USE TEST CARDS:

For SUCCESSFUL Payment:
  Card Number: 4111 1111 1111 1111
  Expiry: 12/25 (any future date)
  CVV: 123
  OTP: 123456
  Result: Payment successful ✅

For FAILED Payment (to test error handling):
  Card Number: 4000 0000 0000 0002
  Expiry: 12/25
  CVV: 123
  Result: Payment failed ✅ (system handles error)
```

---

## 📋 COMPLETE TEST SCENARIOS

### Scenario 1: New User Complete Journey
```
1. ✅ Fresh login & profile completion
2. ✅ Browse 476 internships
3. ✅ Search for specific technology
4. ✅ Apply for internship
5. ✅ View profile with enrolled internship
6. ✅ Submit weekly assignment
7. ✅ Attempt payment (using test card)
8. ✅ View downloaded certificate
```

### Scenario 2: Mobile View Testing
```
1. ✅ Open on mobile device OR DevTools mobile view
2. ✅ Bottom navigation works (Home, Explore, Profile, Menu)
3. ✅ Profile button shows blue when active
4. ✅ Search filters visible (not hidden)
5. ✅ Buttons are clickable (44px+ size)
6. ✅ Forms are fillable
7. ✅ All text is readable
8. ✅ No horizontal scrolling
```

### Scenario 3: Search & Filter Testing
```
1. ✅ Search "Python" → Shows all Python internships
2. ✅ Search "React" → Shows React, Next.js, React Native
3. ✅ Search "Cloud" → Shows AWS, Azure, GCP
4. ✅ Filter by "Backend Development" → Shows 10 internships
5. ✅ Filter by "Frontend Development" → Shows 6 internships
6. ✅ Filter by "C Programming" → Shows 20 internships ✨ NEW
7. ✅ Pagination works
8. ✅ Clear search button works
```

---

## 🔧 TROUBLESHOOTING

### Issue: "Invalid or expired token"

**Cause**: JWT token expired or corrupted

**Quick Fix**:
```javascript
// Open DevTools Console (F12)
// Copy and paste:
localStorage.clear();
sessionStorage.clear();
location.reload();
```

**Then**: Login again

---

### Issue: Application Not Created

**Cause**: User profile incomplete

**Fix**:
1. Go to Profile
2. Check if profile shows enrollment
3. If not, re-login
4. Complete all profile fields
5. Try enrollment again

---

### Issue: Can't see Internships

**Cause**: API not responding or search taking time

**Fix**:
1. Wait 2-3 seconds
2. Refresh page
3. Check browser console (F12) for errors
4. Check if backend is running: http://localhost:5000
5. If not running, start backend: `python -m flask run`

---

### Issue: Certificate Button Not Working

**Cause**: Internship not completed or payment system error

**Fix**:
1. Check if all 4 weeks completed
2. Submit all weekly assignments
3. Check payment system: Payment API endpoint working
4. Try with Razorpay test card
5. Check browser console for errors

---

## ✅ EXPECTED RESULTS

### After Successful Login
```
✅ Token in localStorage
✅ User profile in localStorage
✅ Redirect to home page
✅ "Profile" tab available
```

### After Successful Enrollment
```
✅ Application created
✅ Offer letter generated
✅ Message: "Application created successfully"
✅ Application visible in Profile
✅ Progress bar shows 0%
```

### After Successful Assignment Submission
```
✅ PDF uploaded
✅ Task marked "submitted"
✅ Progress updates (Week 1 of 4)
✅ Message: "Assignment uploaded successfully"
```

### After Successful Payment
```
✅ Payment processed
✅ Certificate status: "ISSUED & PAID"
✅ Certificate download available
✅ Progress shows 100%
```

---

## 📊 TEST METRICS

### Performance
- [ ] Page load < 2 seconds
- [ ] Search results < 1 second
- [ ] Profile page < 1.5 seconds
- [ ] API response < 500ms

### Mobile Responsiveness
- [ ] Buttons all clickable
- [ ] Text all readable
- [ ] No horizontal scroll
- [ ] All features accessible

### Functionality
- [ ] Login works
- [ ] Search works
- [ ] Enrollment works
- [ ] Submissions work
- [ ] Payment works
- [ ] Certificates work

---

## 🚀 FINAL CHECKLIST

Before declaring platform READY:

### Authentication
- [ ] Login with fresh browser
- [ ] Token properly stored
- [ ] Multiple devices can login
- [ ] Logout clears session

### Internships
- [ ] All 476 internships visible
- [ ] All 20 C programming internships visible
- [ ] Search returns correct results
- [ ] Filters work properly
- [ ] Pagination works

### Enrollment
- [ ] Can apply for internship
- [ ] Offer letter generated
- [ ] Application saved to database
- [ ] Progress tracking works
- [ ] Multiple enrollments possible

### Submissions
- [ ] Can upload PDF files
- [ ] File size validated (max 10MB)
- [ ] Task marked submitted
- [ ] Progress updates correctly
- [ ] Submissions saved

### Payment
- [ ] Razorpay modal opens
- [ ] Test card succeeds
- [ ] Test card fails gracefully
- [ ] Payment recorded
- [ ] Certificate issued

### Mobile
- [ ] Profile button blue
- [ ] All tabs visible
- [ ] Search & filters work
- [ ] Enrollment works
- [ ] All buttons clickable

---

## 📞 SUPPORT

If any issue persists:

1. **Check Console**: F12 → Console → Look for errors
2. **Check Network**: F12 → Network → Check API responses
3. **Restart Backend**: Stop and restart Flask server
4. **Clear Cache**: Ctrl+Shift+Delete → Clear everything
5. **Contact**: Check terminal logs for detailed errors

---

## 🎯 SUCCESS INDICATORS

✅ **Platform is working perfectly when:**

1. **Can login**: Authentication successful
2. **Can browse**: 476+ internships visible
3. **Can search**: "C programming" returns 20 results
4. **Can enroll**: Application created without token error
5. **Can submit**: PDF uploads successful
6. **Can pay**: Razorpay payment processes
7. **Can download**: Certificate available

**If all ✅ then platform is PRODUCTION READY!**

---

*Last Updated*: September 12, 2026  
*Testing Version*: Complete  
*Status*: Ready for comprehensive testing ✅
