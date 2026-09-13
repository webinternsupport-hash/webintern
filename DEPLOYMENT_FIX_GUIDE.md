# 🚀 Deployment Guide - Critical Fixes

## Files Modified

These 3 files must be deployed together for fixes to work:

### 1. `/webintern/static/js/views/dashboardView.js`
**What Changed**: Data fetching priority reversed
- **Before**: Load from IndexedDB first (empty), then fetch from server
- **After**: Fetch from server first, fallback to IndexedDB

**Why It Matters**: Users see their actual persisted account data immediately

**Deployment Check**:
```bash
# Verify file exists and has no syntax errors
file webintern/static/js/views/dashboardView.js
# Should see: JavaScript source code
```

### 2. `/webintern/static/js/api.js`
**What Changed**: API requests now use absolute URLs instead of relative paths
- **Before**: `fetch('/api/applications/me')`
- **After**: `fetch(window.location.origin + '/api/applications/me')`

**Why It Matters**: API calls work in production when deployed to domain

**Deployment Check**:
```bash
# Verify file exists and has no syntax errors
file webintern/static/js/api.js
# Search for window.location.origin
grep -n "window.location.origin" webintern/static/js/api.js
```

### 3. `/webintern/static/css/mobile-form-fixes.css`
**What Changed**: Added pointer-events fixes for checkboxes
- **Before**: Checkboxes might be unclickable on mobile
- **After**: Checkboxes always clickable with proper z-index

**Why It Matters**: Mobile users can now check T&C and Marketing checkboxes

**Deployment Check**:
```bash
# Verify CSS file
file webintern/static/css/mobile-form-fixes.css
# Check for pointer-events
grep -n "pointer-events" webintern/static/css/mobile-form-fixes.css
```

---

## Pre-Deployment Checklist

### Code Quality
- [ ] All 3 files modified and saved
- [ ] No trailing whitespace
- [ ] No syntax errors (run diagnostics)
- [ ] All changes are backward compatible
- [ ] No console.log() statements left in production code

### Database
- [ ] SQLite database file exists: `webintern.db`
- [ ] Database has all tables (profiles, applications, etc.)
- [ ] Database is not corrupted
```bash
# Check database
sqlite3 webintern.db ".tables"
sqlite3 webintern.db "SELECT COUNT(*) FROM profiles;"
```

### Environment Configuration
- [ ] `.env` file exists and is configured
- [ ] `SUPABASE_URL` is set (if using Supabase)
- [ ] `SUPABASE_ANON_KEY` is set
- [ ] `RAZORPAY_KEY_ID` is set (for payments)
- [ ] `JWT_SECRET` is set and strong

### Git & Version Control
- [ ] All changes committed to git
- [ ] Version tag created if this is a release
- [ ] Changes documented in commit message

```bash
git status                          # Should show nothing or only expected files
git log --oneline -5               # Verify recent commits
git diff HEAD~1                    # Review what changed
```

---

## Deployment Steps

### Option 1: Vercel / Traditional Hosting

```bash
# 1. Commit all changes
git add webintern/static/js/views/dashboardView.js
git add webintern/static/js/api.js
git add webintern/static/css/mobile-form-fixes.css
git commit -m "CRITICAL FIX: Resolve data persistence, login, checkboxes, API URLs, and mobile layout"

# 2. Push to repository
git push origin main

# 3. Trigger deployment (automatic if using CI/CD)
# Vercel will auto-redeploy on git push
# Or manually deploy from Vercel dashboard
```

### Option 2: Docker Deployment

```bash
# 1. Build new Docker image with latest code
docker build -t webintern:latest .

# 2. Verify image
docker images | grep webintern

# 3. Push to registry (if using registry)
docker push your-registry/webintern:latest

# 4. Update deployment/k8s manifest with new image tag
# Then apply: kubectl apply -f deployment.yaml

# 5. Verify pod is running
kubectl get pods
```

### Option 3: Direct Server Deployment

```bash
# 1. SSH into server
ssh user@your-domain.com

# 2. Navigate to app directory
cd /var/www/webintern

# 3. Pull latest code
git pull origin main

# 4. Restart application
systemctl restart webintern
# OR: supervisorctl restart webintern
# OR: pm2 restart app

# 5. Verify application is running
curl http://localhost:5000/api/auth/config
# Should return JSON with no errors
```

---

## Post-Deployment Verification (CRITICAL)

### Immediate Checks (5 mins)
```bash
# Check if application is running
curl https://your-domain.com/
# Should return HTML (homepage)

# Check API is responding
curl https://your-domain.com/api/auth/config
# Should return JSON

# Check database connection
# (Log into application and check error logs)

# Tail application logs
ssh user@your-domain.com
tail -f /var/log/webintern/app.log
# Should NOT show: 
#   - 500 errors
#   - CORS errors
#   - Database connection errors
```

### Functional Tests (10 mins)
1. **Issue #1 - Data Persistence**
   - [ ] Signup with new email
   - [ ] Enroll in internship
   - [ ] Reload page
   - [ ] ✅ Enrollment still visible

2. **Issue #2 - Login**
   - [ ] Log out
   - [ ] Log in with same credentials
   - [ ] ✅ Should succeed

3. **Issue #3 - Mobile Checkboxes**
   - [ ] Mobile browser (DevTools 375px)
   - [ ] Signup page
   - [ ] ✅ T&C checkbox is clickable

4. **Issue #4 - Buttons Work**
   - [ ] Click "Offer" button
   - [ ] ✅ PDF opens/downloads
   - [ ] Browser console: no CORS errors

5. **Issue #5 - Mobile Profile**
   - [ ] Mobile view
   - [ ] ✅ Enrollments display vertically
   - [ ] ✅ No horizontal scroll

### Performance Check
```bash
# Check page load time
curl -w "@curl-format.txt" -o /dev/null -s https://your-domain.com/
# Should be < 2 seconds

# Check CSS file is loading
curl -I https://your-domain.com/css/mobile-form-fixes.css
# Should return: HTTP/2 200 (not 404)

# Check JS file is loading
curl -I https://your-domain.com/js/api.js
# Should return: HTTP/2 200 (not 404)
```

### Database Verification
```bash
# Check data is being saved
sqlite3 webintern.db "SELECT email FROM profiles LIMIT 5;"
# Should show recently registered emails

# Check applications are being saved
sqlite3 webintern.db "SELECT COUNT(*) FROM applications;"
# Should be > 0 if users have enrolled
```

---

## Monitoring After Deployment

### Key Metrics to Track
1. **Error Rate**: Should be 0 for these fixes
2. **API Response Time**: Should be < 500ms
3. **Page Load Time**: Should be < 2s
4. **Login Success Rate**: Should be 100%
5. **Data Persistence**: Users shouldn't report missing data

### Application Logs to Monitor
```
Pattern: [ERROR]
Pattern: 401 Unauthorized
Pattern: CORS
Pattern: failed
Pattern: exception
Pattern: traceback
```

### User Feedback to Watch For
- ❌ "My data disappeared after reload"
- ❌ "Can't log back in"
- ❌ "Checkboxes don't work on mobile"
- ❌ "Certificate button doesn't work"
- ❌ "Can't see my internship on mobile"

---

## Rollback Plan

If something breaks after deployment:

### Quick Rollback (Git)
```bash
# Revert the last commit
git revert HEAD
git push origin main

# Vercel/CI will auto-redeploy previous version
```

### Emergency Rollback (Docker)
```bash
# Rollback to previous image
docker run -d -p 5000:5000 webintern:previous-tag

# Or use kubernetes rollout
kubectl rollout undo deployment/webintern
```

### Manual Rollback (Server)
```bash
# Restore from backup
git reset --hard HEAD~1
git push -f origin main
systemctl restart webintern

# Verify
curl https://your-domain.com/
```

---

## Common Deployment Issues & Fixes

### Issue: CORS Errors in Browser Console
```
ERROR: Access-Control-Allow-Origin header missing
```

**Fix**:
```python
# Verify app.py has CORS enabled
CORS(app, supports_credentials=True)

# Restart application
systemctl restart webintern
```

### Issue: API Calls Return 404
```
Network: /api/applications/me - 404 Not Found
```

**Fix**:
```bash
# Check if API blueprints are registered in app.py
grep "register_blueprint" webintern/app.py

# Verify database file exists
ls -la webintern.db

# Restart application
systemctl restart webintern
```

### Issue: Checkboxes Still Not Clickable on Mobile
```
CSS not loading or not applied
```

**Fix**:
```bash
# Verify CSS file is being loaded in index.html
grep "mobile-form-fixes.css" webintern/static/index.html

# Clear browser cache
# DevTools: Network → Disable cache → Reload
# Or: Shift + Reload (hard refresh)

# Verify CSS file has pointer-events fix
grep "pointer-events" webintern/static/css/mobile-form-fixes.css
```

### Issue: Data Not Persisting After Login
```
Dashboard shows "No Active Internships" after login
```

**Fix**:
1. Check if `/api/applications/me` returns data
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" https://your-domain.com/api/applications/me
   ```

2. Check if database has data
   ```bash
   sqlite3 webintern.db "SELECT * FROM applications WHERE user_id = 'USER_ID';"
   ```

3. Verify dashboardView.js has latest code
   ```bash
   grep "serverFetchSucceeded" webintern/static/js/views/dashboardView.js
   ```

---

## Deployment Success Criteria

✅ **All criteria must be met before considering deployment successful**:

- [ ] No 500 errors in application logs
- [ ] No CORS errors in browser console
- [ ] Signup works end-to-end
- [ ] Login works end-to-end
- [ ] Data persists after reload
- [ ] Mobile view works without horizontal scroll
- [ ] Checkboxes are clickable on mobile
- [ ] API buttons work (Offer, Cert, Tasks)
- [ ] Database has saved user records
- [ ] Page loads in under 2 seconds
- [ ] All API calls return 200 status

---

## Final Sign-Off

**Deployment Date**: _______________
**Deployed By**: _______________
**Verification Completed By**: _______________
**All Tests Passed**: ☐ YES ☐ NO

**Comments**:
```




```

**Ready for Production Traffic**: ☐ YES ☐ NO - Needs fixes (describe below):
```




```

---

## Support Escalation

If deployment fails:

1. Check all 3 files are deployed
2. Review deployment logs
3. Check database connectivity
4. Verify environment variables
5. Review browser console errors
6. Check Network tab for failed requests
7. Escalate to backend team if database issues
8. Escalate to DevOps if deployment infrastructure issues

---

## Document Version
- Created: September 14, 2026
- Status: Ready for Deployment
- Changes: Critical Issues Fix #1-5
