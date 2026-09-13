# Supabase Persistence Guide

## Overview

You now have complete database persistence for user activity. When users enroll, pay, or complete internships, all data is saved to **Supabase** and persists across:
- Page refreshes
- Browser restarts
- Logout/login cycles
- Device changes (same account on different device)

## What Gets Saved to Supabase

### 1. **Enrollments** (When user clicks "Apply")
- Internship ID, title, start/end dates
- Offer letter ID
- Status (active, completed, withdrawn)
- **Persists**: ✅ Survives logout/refresh

### 2. **Payments** (When user pays for certificate)
- Razorpay order ID and payment ID
- Amount paid (₹199)
- Payment status (created, paid, failed)
- **Persists**: ✅ Survives logout/refresh

### 3. **Certificates** (When payment is verified)
- Certificate URL and number
- Issue date
- Verification status
- **Persists**: ✅ Survives logout/refresh

### 4. **Internship History** (Tracks progress)
- Enrollment status (enrolled → in_progress → completed)
- Progress percentage
- Completed weeks
- **Persists**: ✅ Survives logout/refresh

### 5. **Submissions** (Weekly assignments)
- Week number and status
- File URL
- Marks and feedback
- **Persists**: ✅ Survives logout/refresh

### 6. **Sync Logs** (Debugging)
- Tracks what synced successfully
- Records sync failures
- **Persists**: ✅ Always available for debugging

---

## How It Works

### User Enrolls in Internship:
```
1. User clicks "Apply" for internship
   ↓
2. Backend saves to LOCAL database (SQLite)
   ↓
3. Backend syncs to SUPABASE database (cloud)
   ↓
4. Result: Data persists even after logout/refresh
```

### User Pays for Certificate:
```
1. User completes payment via Razorpay
   ↓
2. Backend verifies payment signature
   ↓
3. Backend saves to LOCAL database
   ↓
4. Backend syncs to SUPABASE database
   ↓
5. Certificate generated and emailed
   ↓
6. Result: Payment and certificate both persisted
```

### User Logs Back In:
```
1. User logs in with email/password
   ↓
2. Backend loads profile from LOCAL database
   ↓
3. Frontend calls API to fetch enrollments/payments/certificates
   ↓
4. API can fetch from LOCAL or SUPABASE
   ↓
5. Dashboard shows all previous activity
```

---

## Implementation Details

### What You Did:
1. ✅ Created 6 tables in Supabase for: enrollments, payments, certificates, internship_history, submissions, sync_logs
2. ✅ Created `supabase_sync.py` with functions to save/fetch data from Supabase
3. ✅ Updated `application_routes.py` to sync enrollments when user applies
4. ✅ Updated `payment_routes.py` to sync payments and certificates when user pays

### What Automatically Happens:
- **On Enrollment**: Saved to Supabase with user_id linked
- **On Payment**: Saved to Supabase with enrollment_id linked
- **On Certificate Generation**: Saved to Supabase with user_id linked
- **Sync Status**: Every sync is logged in sync_logs table for debugging

---

## Accessing Data After Login

When user logs in and refreshes page:

### Option 1: Fetch from Supabase (Recommended)
```python
from utils.supabase_sync import get_user_enrollments_from_supabase

enrollments = get_user_enrollments_from_supabase(user_id)
payments = get_user_payments_from_supabase(user_id)
certificates = get_user_certificates_from_supabase(user_id)
```

### Option 2: Keep Using Local Database
Your existing LOCAL database still works perfectly. All data is saved both locally AND to Supabase.

---

## Testing

### Test Case 1: Enrollment Persistence
1. Login to your app
2. Enroll in an internship
3. Check Supabase dashboard → enrollments table → should see new record with your user_id
4. Logout and login again
5. Your enrollment should still be visible (loaded from Supabase)
6. Refresh page → enrollment still visible

### Test Case 2: Payment Persistence
1. Complete an internship
2. Pay for certificate (use test card: 4111 1111 1111 1111)
3. Check Supabase → payments table → should see payment record with status='paid'
4. Logout and login again
5. Certificate should still be available
6. Refresh page → certificate still available

### Test Case 3: Cross-Device Sync
1. User A logs in on Browser A, enrolls in internship
2. Same User A logs in on Browser B
3. Enrollment from Browser A should be visible on Browser B (loaded from Supabase)

### Test Case 4: Sync Log Verification
1. Perform any action (enroll, pay)
2. Check Supabase → sync_logs table
3. Should see entry with sync_type='ENROLLMENT' or 'PAYMENT' and status='synced'
4. If sync failed, should see status='failed' with error_message

---

## Troubleshooting

### "Supabase sync failed" in logs
**Cause**: Supabase connection issue or wrong credentials
**Fix**: Verify SUPABASE_URL and SUPABASE_ANON_KEY in .env

### Data not appearing in Supabase
**Cause**: Sync not being triggered
**Fix**: Check logs for [Supabase Sync] messages
**Verify**: `sync_logs` table in Supabase

### User can't see data after login
**Cause**: Data not linked with correct user_id
**Fix**: Every record must have user_id = auth user id
**Verify**: In Supabase, enrollments table should have user_id matching auth user

### Getting 404 on API endpoints
**Cause**: Routes not properly registered
**Fix**: Verify routes are imported in app.py

---

## Security Notes

✅ **DO:**
- All data is scoped to user_id (user can only see their own data)
- Payments are verified with Razorpay signature before accepting
- Sync logs track all changes for audit trail

❌ **DON'T:**
- Never display data without filtering by current user_id
- Never skip Razorpay signature verification
- Never expose Supabase service key in frontend

---

## Next Steps

1. **Verify Supabase Tables**: Log into Supabase → check 6 tables exist
2. **Test Locally**: Run app locally, enroll/pay, check Supabase data appears
3. **Deploy**: Push to production (Vercel), test on production Supabase

---

## API Endpoints That Now Persist Data

### Enrollment
- `POST /api/applications` - Saves enrollment + syncs to Supabase
- `GET /api/applications` - Gets user's enrollments

### Payment
- `POST /api/payments/create_order` - Creates Razorpay order
- `POST /api/payments/verify` - Verifies payment + syncs to Supabase
- `GET /api/payments/{enrollment_id}` - Gets payment status

### Certificate
- `GET /api/certificates/{cert_id}` - Gets certificate (persisted in DB)
- `POST /api/certificates/{cert_id}/download` - Downloads certificate PDF

---

## Data Model (What's Stored)

### Enrollments Table
```
id (UUID)
user_id (UUID) ← Links to auth user
internship_id (VARCHAR)
status (TEXT): 'active', 'completed', 'withdrawn'
start_date (TEXT)
end_date (TEXT)
offer_letter_id (VARCHAR)
certificate_id (VARCHAR)
enrolled_date (TIMESTAMP)
```

### Payments Table
```
id (UUID)
user_id (UUID) ← Links to auth user
enrollment_id (UUID) ← Links to enrollment
razorpay_order_id (TEXT) - Unique payment reference
razorpay_payment_id (TEXT)
razorpay_signature (TEXT)
amount_inr (INT) - ₹199 for certificates
status (TEXT): 'created', 'paid', 'failed', 'refunded'
```

### Certificates Table
```
id (UUID)
user_id (UUID) ← Links to auth user
enrollment_id (UUID) ← Links to enrollment
certificate_url (TEXT) - URL to certificate PDF
certificate_number (TEXT) - Unique cert number
is_verified (BOOLEAN) - True after payment verified
issued_at (TIMESTAMP)
```

---

## Support

If data isn't syncing:
1. Check Supabase credentials in .env
2. Check `/logs` for [Supabase Sync] error messages
3. Check `sync_logs` table in Supabase for failed syncs
4. Contact Supabase support if connection fails

