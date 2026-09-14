# CRITICAL ISSUES - FIX IMPLEMENTATION GUIDE

## Issue #1: Data Persistence (PRIMARY - CRITICAL)

**Problem**: Data is not being restored after user login/reload. User sees empty dashboard.

**Root Causes**:
1. Dashboard loads persisted IndexedDB first (empty for new users), then tries to fetch from server
2. If IndexedDB is empty, it displays empty state instead of waiting for server data
3. Server data fetch might fail silently due to incorrect API base URL in production

**Fixes**:
- dashboardView.js: Priority should be: fetch from server FIRST, then use persisted as fallback
- Ensure API calls use correct absolute paths that work in production
- Store fetched server data in IndexedDB for offline access

**Files to Fix**:
- `/webintern/static/js/views/dashboardView.js` - Priority: fetch server data FIRST
- `/webintern/static/js/api.js` - Ensure API base URL is correct

---

## Issue #2: Login Failure After Account Creation

**Problem**: After registering, user cannot log back in with same credentials.

**Root Causes**:
1. SQLite DB might not be properly initialized on first run
2. Password hash mismatch between registration and login
3. JWT token validation might be broken
4. Email case sensitivity issues

**Fixes**:
- Verify password hashing uses same algorithm on register and login
- Ensure email comparison is case-insensitive
- Check JWT token is being set properly in cookies/localStorage

**Files to Check**:
- `/webintern/routes/auth_routes.py` - Register and login endpoints
- `/webintern/database.py` - Ensure SQLite schema is created properly

---

## Issue #3: Mobile Checkboxes Not Clickable

**Problem**: T&C checkboxes on mobile signup form don't respond to taps.

**Root Causes**:
1. CSS might have pointer-events: none or z-index issue
2. Label might be overlaying checkbox
3. Touch-action not set correctly
4. Mobile viewport scaling issue

**Fixes**:
- Ensure checkbox has pointer-events: auto
- Increase touch target to 44x44px minimum
- Check label click handler works with checkboxes
- Verify checkbox is not hidden behind label

**File to Fix**:
- `/webintern/static/css/mobile-form-fixes.css` - Already has good styling, verify it's loaded
- `/webintern/static/js/views/authViews.js` - Ensure form binding works for mobile

---

## Issue #4: Buttons Not Working Post-Deployment

**Problem**: Offer Letter, Task, Certificate buttons don't work after deployment to live site.

**Root Causes**:
1. API base URL might be relative path instead of absolute
2. CORS issues between frontend and backend
3. Environment variables not set correctly on production
4. API endpoints using localhost instead of deployment URL

**Fixes**:
- Use absolute API paths: `/api/...` instead of relative paths
- Verify CORS headers are set correctly in production
- Check environment variables are loaded from .env
- Ensure all URLs use https:// on production

**Files to Fix**:
- `/webintern/static/js/api.js` - Ensure API.request() uses correct base URL
- `/webintern/static/js/views/dashboardView.js` - Button action handlers
- `/webintern/app.py` - CORS configuration
- `/webintern/config.py` - Environment variable loading

---

## Issue #5: Mobile Profile Page - Enrolled Internships Not Displaying

**Problem**: In mobile view, Profile page doesn't show enrolled internship details properly.

**Root Causes**:
1. Mobile CSS might not have proper grid/flex for enrollment cards
2. Data might not be fetched before rendering
3. Layout might be broken for small screens
4. Enrollment data might not be in correct format

**Fixes**:
- Ensure enrollment display uses mobile-optimized layout
- Stack cards vertically on mobile (not grid)
- Ensure min-height is correct so content is not hidden
- Test data flow from API to display

**Files to Fix**:
- `/webintern/static/js/views/dashboardView.js` - Profile section rendering
- `/webintern/static/css/mobile-app.css` - Mobile layout for enrollment cards

---

## Implementation Priority:
1. Issue #1 (Data Persistence) - MUST FIX FIRST - foundational
2. Issue #4 (Post-Deployment URLs) - FIX IMMEDIATELY - affects production
3. Issue #2 (Login) - FIX SECOND - likely stemming from #1
4. Issue #3 (Mobile Checkboxes) - FIX THIRD - mobile UX
5. Issue #5 (Mobile Profile) - FIX FOURTH - mobile display

---

## Testing Checklist After Fixes:
- [ ] Register new account → data saves to DB
- [ ] Log out → log in again with same credentials → succeeds
- [ ] Enroll in internship → reload page → enrollment still shows
- [ ] Make payment → reload page → payment status persists
- [ ] Mobile: tap T&C checkboxes → respond to clicks
- [ ] Live site: click Offer Letter → opens PDF
- [ ] Live site: click Certificate → opens payment modal or PDF
- [ ] Live site: click Tasks → opens workspace
- [ ] Mobile Profile: enrolled internship details visible and formatted correctly
