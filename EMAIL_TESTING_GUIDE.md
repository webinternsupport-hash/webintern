# Email Integration Testing Guide

## Quick Start - Testing Email Workflows

### Prerequisites
- ✓ Flask app running on http://127.0.0.1:5000
- ✓ RESEND_API_KEY configured in `.env` file
- ✓ Database initialized with tables
- ✓ Student account created
- ✓ Internships available

## Test Flow 1: Offer Letter Email (On Application)

### Steps
1. **Create Student Account** (if not already done)
   - Sign up with valid email (preferably a real email you can check)
   - Complete profile setup

2. **Apply for Internship**
   - Navigate to explore internships
   - Select any internship
   - Click "Apply" or "Enroll"
   - Complete application form
   - Submit

3. **Check for Email**
   - Check your inbox for email from `Web Intern <notifications@webintern.in>`
   - Subject: "Your WebIntern Internship Offer Letter"
   - Verify attachment: PDF file named `WebIntern_Offer_Letter_WI-OFFER-*.pdf`
   - Verify content includes:
     * Internship title
     * Start date
     * End date
     * Duration
     * Offer ID

4. **Verify in Database**
   ```sql
   SELECT * FROM documents 
   WHERE document_type = 'OFFER_LETTER' 
   ORDER BY created_at DESC 
   LIMIT 1;
   ```
   Expected:
   - `email_status`: 'SENT' (if successful) or 'FAILED'
   - `email_message_id`: Resend message ID
   - `file_path`: Path to generated PDF

5. **Check Console Logs**
   Look for output like:
   ```
   [Email Thread] Started for application [app_id]
   [✅ EMAIL SENT] To: [student_email], ID: [resend_msg_id]
   ```

---

## Test Flow 2: Certificate Email (On Payment)

### Prerequisites
- ✓ Student has active application/enrollment
- ✓ Internship tasks completed (or in test mode, skip this)
- ✓ Ready for certificate payment

### Steps

1. **Navigate to Certificate Payment**
   - Go to student dashboard
   - Find enrolled internship
   - Click "Get Certificate" or "Certificate Payment"
   - Review fee: ₹199

2. **Initiate Payment**
   - Click "Pay for Certificate"
   - Razorpay payment window opens
   - Use test card: `4111 1111 1111 1111`
   - Expiry: Any future date (e.g., 12/25)
   - CVV: Any 3 digits (e.g., 123)
   - Name: Any name

3. **Complete Payment**
   - Payment processes
   - You should be redirected back to app
   - Certificate issued message shown

4. **Check for Certificate Email**
   - Check inbox for email from `Web Intern <notifications@webintern.in>`
   - Subject: "Your WebIntern Internship Completion Certificate"
   - Verify attachment: PDF file named `WebIntern_Certificate_WI-CERT-*.pdf`
   - Verify content includes:
     * Student name
     * Internship title
     * Certificate ID
     * Issue date
     * Verification link
     * QR code (if available)

5. **Verify in Database**
   ```sql
   SELECT * FROM documents 
   WHERE document_type = 'CERTIFICATE' 
   ORDER BY created_at DESC 
   LIMIT 1;
   ```
   Expected:
   - `email_status`: 'SENT' (if successful) or 'FAILED'
   - `email_message_id`: Resend message ID
   - `status`: 'ISSUED'

   Also check certificates table:
   ```sql
   SELECT * FROM certificates 
   ORDER BY issued_at DESC 
   LIMIT 1;
   ```
   Expected:
   - `is_verified_paid`: 1 (true)
   - `certificate_url`: URL path to certificate

6. **Verify Certificate Signature**
   - Click verification link in email
   - Should display certificate details and verification status

---

## Troubleshooting

### Issue: Email not received
**Check 1: Resend API Key**
```sql
-- Verify API key is set (won't show actual value)
SELECT CASE WHEN LENGTH(RESEND_API_KEY) > 0 THEN 'CONFIGURED' ELSE 'NOT CONFIGURED' END FROM config;
```

**Check 2: Console Logs**
Look for:
- `[❌ EMAIL BLOCKED] RESEND API KEY NOT CONFIGURED` → Add API key to `.env`
- `[❌ EMAIL FAILED] HTTP 401` → Invalid API key
- `[❌ EMAIL FAILED] HTTP 422` → Invalid email format or other validation error
- `[❌ EMAIL EXCEPTION]` → Network or other error

**Check 3: Resend Dashboard**
- Go to https://resend.com/emails
- Check email log for failed deliveries
- Look for bounce notifications

### Issue: Email marked as FAILED in database
```sql
SELECT * FROM documents 
WHERE email_status = 'FAILED' 
ORDER BY updated_at DESC 
LIMIT 1;
```

Possible causes:
- Invalid recipient email address
- Email domain not verified in Resend
- API quota exceeded
- Network timeout

**Solution: Admin Resend**
```
POST /api/admin/payments/{payment_id}/resend-certificate
```

### Issue: PDF not attached to email
- Check if PDF generation is working
- Verify PDF file exists at path shown in database
- Check console for `[PDF Generation Error]`

### Issue: Payment not triggering certificate email
- Verify payment status is 'paid' in database
- Check Razorpay webhook is configured
- Verify signature validation passed

---

## Manual Testing (Without Email)

If you don't have a real email to test:

1. **Check Database Directly**
   - Documents are saved to database even if email fails
   - PDFs are generated and cached on disk

2. **View Generated PDF**
   - Offer letter: `/storage/generated/offers/offer_{app_id}.pdf`
   - Certificate: `/storage/generated/certificates/certificate_{cert_id}.pdf`
   - Download via API: `/api/applications/{app_id}/offer-letter.pdf`

3. **Simulate Email Success in Database**
   ```sql
   UPDATE documents 
   SET email_status = 'SENT', 
       email_message_id = 'email_test_' || date('now')
   WHERE document_type = 'OFFER_LETTER' 
   AND email_status = 'FAILED' 
   LIMIT 1;
   ```

---

## Performance Monitoring

### Email Dispatch Time
Should complete in < 100ms (response returned before email sent)

Check in console:
```
[✅ EMAIL SENT] To: [email], ID: [id]
```
Time between application submission and this log indicates dispatch time.

### Resend API Response Time
- Typical: 100-500ms
- Acceptable: < 2 seconds
- Issues if: > 5 seconds

### Email Delivery Time
- Typical: < 1 minute
- Fast: < 10 seconds
- Delayed: > 5 minutes (check Resend logs)

---

## Testing Checklist

- [ ] Offer Letter Email Test
  - [ ] Email received
  - [ ] Contains correct internship details
  - [ ] PDF attachment present
  - [ ] Database shows SENT status

- [ ] Certificate Email Test  
  - [ ] Payment processed successfully
  - [ ] Certificate email received
  - [ ] Contains correct certificate details
  - [ ] PDF attachment present
  - [ ] Verification link works
  - [ ] Database shows SENT status

- [ ] Error Handling
  - [ ] Invalid email shows graceful error
  - [ ] Failed emails can be resent via admin API
  - [ ] Console logs are informative

- [ ] Multi-Device Testing
  - [ ] Email received on phone
  - [ ] Email received on desktop
  - [ ] PDF can be opened on different devices
  - [ ] Links work across devices

---

## Next Steps After Testing

1. ✓ Verify both email flows work correctly
2. ✓ Test on mobile devices and different email clients
3. ✓ Prepare production credentials:
   - Production Resend API key
   - Production Razorpay credentials
   - Production email domain
4. ✓ Update `.env` with production values
5. ✓ Set up monitoring/alerts for failed emails
6. ✓ Deploy to production
7. ✓ Monitor first week of email delivery

---

## Support Resources

- **Resend API Docs**: https://resend.com/docs
- **Resend Email Dashboard**: https://resend.com/emails
- **Razorpay Docs**: https://razorpay.com/docs
- **Razorpay Dashboard**: https://dashboard.razorpay.com

---

**Status**: Email integration is COMPLETE and ready for testing.
