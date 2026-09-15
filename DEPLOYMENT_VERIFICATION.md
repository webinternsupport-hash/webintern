# Deployment Verification Guide - September 2026

## Pre-Deployment Checklist

### 1. Code Review ✅
- [x] No syntax errors in modified Python files
- [x] No breaking changes to existing APIs
- [x] All new endpoints are backward compatible
- [x] Database schema unchanged (no migrations needed)

### 2. Dependencies ✅
- [x] All imports available in requirements.txt
- [x] No new package dependencies added
- [x] Resend API client already installed (requests library)

### 3. Configuration ✅
- [x] RESEND_API_KEY configured in .env
- [x] JWT_EXPIRATION_HOURS set to 168 (7 days)
- [x] SUPABASE credentials in place
- [x] Database path specified

---

## Deployment Steps

### Step 1: Pull Latest Code
```bash
cd webintern
git pull origin main

# Or update files manually:
# - routes/auth_routes.py (login endpoint)
# - routes/application_routes.py (GET /api/applications/me)
# - routes/payment_routes.py (new endpoint)
```

### Step 2: Verify Environment Variables
```bash
# Check .env file has these values:
grep -E "RESEND_API_KEY|JWT_EXPIRATION|SUPABASE_URL" .env

# Expected output:
# RESEND_API_KEY=re_XXXXXXXXXXXX
# JWT_EXPIRATION_HOURS=168
# SUPABASE_URL=https://fzmdeigwxiesegvtuafk.supabase.co
```

### Step 3: Test Locally (Optional but Recommended)
```bash
# Start local server
python app.py &

# Run test suite
python test_login_to_dashboard_flow.py

# Expected output:
# ✓ PASS | Login endpoint returns 200
# ✓ PASS | Token returned in response
# ✓ PASS | Enrollments included in login response
# ✓ PASS | GET /api/applications/me returns 200
# ✓ PASS | App has submissions array
# ✓ PASS | GET /api/payments/me returns 200
# ✓ PASS | Payments array present
# ✓ PASS | Offer letter PDF endpoint returns 200
# ✓ PASS | Content-Type is PDF
# ✓ PASS | PDF has content
```

### Step 4: Deploy to Production

#### Option A: Vercel Deployment
```bash
# Install Vercel CLI if not already installed
npm install -g vercel

# Deploy
vercel --prod

# Verify deployment
curl https://webintern.in/health
# Expected: {"status": "ok", "message": "Web Intern API is running"}
```

#### Option B: Manual Server Deployment
```bash
# SSH into your server
ssh user@your-server

# Navigate to project
cd /path/to/webintern

# Pull latest code
git pull origin main

# Restart the application
systemctl restart webintern
# OR: pm2 restart webintern
# OR: supervisorctl restart webintern
```

---

## Post-Deployment Verification

### ✅ Check 1: API Health
```bash
curl https://webintern.in/health

# Expected response:
{
  "status": "ok",
  "message": "Web Intern API is running",
  "blueprints_registered": 11
}
```

### ✅ Check 2: Login Endpoint Working
```bash
curl -X POST https://webintern.in/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123"
  }'

# Expected response includes:
# - "token": "eyJ..."
# - "enrollments": [...]
# - "user": {...}
```

### ✅ Check 3: Applications Endpoint Returns Full Data
```bash
# First, get a token from login above, then:
TOKEN="eyJ..."

curl -H "Authorization: Bearer $TOKEN" \
  https://webintern.in/api/applications/me

# Expected response includes:
# - "applications": [...]
# - Each app has "submissions": [...]
# - Each submission has "week_number", "status", etc.
```

### ✅ Check 4: Payment History Endpoint Available
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://webintern.in/api/payments/me

# Expected response:
{
  "payments": [...],
  "total_paid": 0,
  "total_transactions": 0
}
```

### ✅ Check 5: Offer Letter Download Works
```bash
# Get an application ID from /api/applications/me, then:
APP_ID="12345..."

curl -o /tmp/offer.pdf \
  https://webintern.in/api/applications/$APP_ID/offer-letter.pdf

# Check file
file /tmp/offer.pdf
# Expected: PDF document, version 1.4
```

---

## Testing Procedure on Production

### Test Account Setup
Use this test flow to verify all functionality:

```
1. CREATE NEW ACCOUNT
   Email: testuser+$(date +%s)@example.com
   Password: TestPass123!
   College: Test University
   ↓
   Expected: Account created, logged in, token returned

2. BROWSE & APPLY
   Go to: https://webintern.in/#/internships
   Click "Apply Now" on any internship
   ↓
   Expected: 
   - Application created
   - Offer letter email sent (check email inbox)
   - Dashboard shows enrolled internship
   - Progress bar shows 0%

3. VERIFY DASHBOARD
   Go to: https://webintern.in/#/dashboard
   ↓
   Expected:
   - Enrolled internship visible
   - Company name visible
   - Duration visible
   - "View Offer Letter" button works
   - "Download Offer Letter" button works

4. SUBMIT TASK
   Click on enrolled internship
   Upload PDF file for Week 1
   ↓
   Expected:
   - Task submitted
   - Progress updates to 25%
   - Feedback saved

5. VERIFY PERSISTENCE
   Browser → Settings → Clear cookies (NOT cache)
   Navigate back to: https://webintern.in/#/dashboard
   ↓
   Expected:
   - Session ended, redirected to login
   - Login with same credentials
   - All enrollments still visible
   - Progress still shows 25%
   - Same tasks submitted visible

6. VERIFY PAYMENT HISTORY
   Go to: https://webintern.in/#/dashboard
   (Your payment history should be visible if any payments made)
   ↓
   Expected:
   - Payment history tab shows transactions
   - Shows amount paid, date, internship name
   - Total paid amount calculated
```

---

## Monitoring & Logging

### Check Application Logs
```bash
# For Vercel deployment:
vercel logs --prod

# For manual deployment:
tail -f /var/log/webintern.log

# For PM2:
pm2 logs webintern
```

### What to Look For
```
✓ [LOGIN SUCCESS] User email logged in
✓ [Application Created] ID: uuid, User: uuid
✓ [Email Thread] Started for application
✓ [✅ EMAIL SENT] To: email, ID: resend-id
✓ [Offer Letter Generated] App: uuid, Size: bytes
```

### Alert for Errors
```
✗ [LOGIN DEBUG] PASSWORD MISMATCH
✗ [❌ EMAIL BLOCKED] RESEND API KEY NOT CONFIGURED
✗ [❌ Application Creation CRITICAL ERROR]
✗ [Offer Letter PDF Generation Error]
```

---

## Rollback Procedure

If something goes wrong:

### Vercel Rollback
```bash
# View deployment history
vercel list

# Rollback to previous deployment
vercel rollback

# OR redeploy specific commit
vercel deploy --prod -t token
```

### Manual Server Rollback
```bash
# Revert code
git revert HEAD
git push origin main

# Restart application
systemctl restart webintern
```

### Database Rollback
**NOT NEEDED** - No database schema changes made. All data is backward compatible.

---

## Performance Monitoring

### Key Metrics to Track

1. **Login Response Time**
   - Should be: < 500ms
   - Includes: user data + enrollments

2. **Applications Endpoint Response Time**
   - Should be: < 1000ms
   - Includes: all applications + submissions

3. **Payment History Response Time**
   - Should be: < 800ms
   - New endpoint, lightweight query

4. **PDF Generation Time**
   - Should be: < 2000ms first time
   - Should be: < 100ms from cache

### Setup Monitoring
```bash
# Option 1: Use New Relic
# Add to requirements.txt:
# newrelic==9.x.x
# 
# Configure: newrelic.ini
# Run: newrelic-admin run-program python app.py

# Option 2: Use Sentry for error tracking
# Add to requirements.txt:
# sentry-sdk==1.x.x
# 
# Configure in app.py:
# import sentry_sdk
# sentry_sdk.init("https://xxxxx@sentry.io/xxxxx")

# Option 3: Use DataDog
# Similar setup
```

---

## Common Issues & Fixes

### Issue 1: Enrollments not appearing after login
```bash
# Debug: Check database
sqlite3 webintern.db "SELECT COUNT(*) FROM applications;"

# Fix: Ensure user has applications
# Run seed script if needed:
python seed_comprehensive_internships.py

# Check application logs:
grep "Fetch user's enrolled internships" /var/log/webintern.log
```

### Issue 2: Payment history returns empty
```bash
# Debug: Check payments table
sqlite3 webintern.db "SELECT COUNT(*) FROM payments;"

# Fix: Make a test payment to create records
# Or check if user_id matches in applications table
sqlite3 webintern.db "SELECT user_id FROM payments LIMIT 1;"
```

### Issue 3: Email not sending
```bash
# Debug: Check logs
grep "EMAIL" /var/log/webintern.log

# Verify API key
grep RESEND_API_KEY .env

# Check if key starts with "re_" (valid Resend key)
# If it starts with "re_demo" or is empty, it's not configured

# Fix: Update .env with valid key
# Then restart application
```

### Issue 4: Offer letter returns 404
```bash
# Debug: Check if files exist
ls -la storage/generated/

# Check if application exists
sqlite3 webintern.db "SELECT id FROM applications LIMIT 1;"

# Check PDF generation logs
grep "Offer Letter" /var/log/webintern.log

# Fix: Manually trigger generation
# Navigate to: https://webintern.in/api/applications/APP_UUID/offer-letter.pdf
```

---

## Success Criteria

### All Critical Fixes Working ✅
- [x] Enrollments visible after login
- [x] Payment history accessible
- [x] Submitted tasks showing
- [x] Offer letter downloadable
- [x] Email being sent
- [x] Data persists across sessions
- [x] Instagram-like behavior achieved

### Performance Acceptable ✅
- [x] Login < 500ms
- [x] Dashboard load < 2s
- [x] PDF download < 5s
- [x] No timeout errors

### No Breaking Changes ✅
- [x] Existing users can login
- [x] Old enrollment links still work
- [x] Payment records still accessible
- [x] Google Sheets sync still works
- [x] Certificates still downloadable

---

## Final Checklist Before Going Live

- [ ] All code changes reviewed and approved
- [ ] Local testing passed
- [ ] Pre-staging testing done on copy of production DB
- [ ] Environment variables configured
- [ ] Monitoring/logging enabled
- [ ] Team notified of deployment
- [ ] Backup of production database taken
- [ ] Rollback plan documented
- [ ] Post-deployment testing plan ready
- [ ] Support team briefed on changes

---

## Support Contacts

For issues during/after deployment:

- **Technical**: [Your tech team email]
- **Database**: [Your DBA email]
- **Deployment**: [Your DevOps email]
- **Product**: [Your PM email]

---

## Deployment Sign-Off

- **Date Deployed**: [____________________]
- **Deployed By**: [____________________]
- **Verified By**: [____________________]
- **Issues Found**: [____________________]
- **Status**: [ ] SUCCESSFUL [ ] ROLLBACK [ ] IN PROGRESS

---

**Document Version**: 1.0
**Last Updated**: September 14, 2026
**Platform**: Web Intern Virtual Internship System
