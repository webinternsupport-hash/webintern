# Local Testing Guide - Complete Feature Verification

## Quick Start: Test Without Razorpay

For immediate local testing without setting up Razorpay, follow this guide.

---

## Test 1: User Registration & Google Login

### Manual Registration (Email/Password)
```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test Student",
    "email": "student@test.com",
    "phone": "+919876543210",
    "college": "ABC Engineering College",
    "department": "Computer Science",
    "password": "TestPass123",
    "confirm_password": "TestPass123",
    "terms_accepted": true
  }'
```

**Expected Response:**
```json
{
  "message": "Registration successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid-here",
    "email": "student@test.com",
    "full_name": "Test Student",
    "profile_complete": true
  }
}
```

### Save Token
```bash
# Use this token for subsequent requests
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## Test 2: Profile Completion After Google Login

### Simulate Google Login (No actual Google signup needed)

```bash
# Step 1: Frontend receives Google credentials
# Step 2: Backend creates incomplete profile
# Step 3: Call complete-profile endpoint

curl -X POST http://127.0.0.1:5000/api/auth/complete-profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "full_name": "Google User",
    "phone": "+919876543210",
    "phone_country_code": "+91",
    "college": "IIT Delhi",
    "department": "Electrical Engineering",
    "degree": "B.Tech"
  }'
```

**Expected Response:**
```json
{
  "message": "Profile completed successfully!",
  "user": {
    "profile_complete": true,
    "college": "IIT Delhi",
    "department": "Electrical Engineering"
  }
}
```

---

## Test 3: Get Current User (Verify Profile)

```bash
curl http://127.0.0.1:5000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "user": {
    "id": "uuid",
    "full_name": "Test Student",
    "email": "student@test.com",
    "phone": "+919876543210",
    "college": "ABC Engineering College",
    "department": "Computer Science",
    "profile_complete": true,
    "role": "student"
  }
}
```

---

## Test 4: Browse Internships

```bash
# Get all internships
curl http://127.0.0.1:5000/api/internships

# Search specific internship
curl "http://127.0.0.1:5000/api/internships?search=python"

# Get internship detail
curl http://127.0.0.1:5000/api/internships/python-internship
```

---

## Test 5: Apply for Internship (Create Application)

First, get an internship ID:

```bash
curl http://127.0.0.1:5000/api/internships | jq '.internships[0].id'
```

Then apply:

```bash
curl -X POST http://127.0.0.1:5000/api/applications \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "internship_id": "INTERNSHIP_ID_HERE"
  }'
```

**Expected Response:**
```json
{
  "message": "Application & Enrollment submitted successfully!",
  "application": {
    "id": "app-uuid",
    "user_id": "student-uuid",
    "internship_id": "internship-uuid",
    "status": "active",
    "start_date": "December 14, 2024",
    "end_date": "January 11, 2025",
    "offer_letter_id": "WI-OFFER-2026-XXXXX",
    "certificate_id": "WI-CERT-2026-XXXXX"
  }
}
```

**Save Application ID:**
```bash
export APP_ID="app-uuid-from-response"
```

---

## Test 6: Get Offer Letter (Document Access)

```bash
# List all your applications
curl http://127.0.0.1:5000/api/applications/me \
  -H "Authorization: Bearer $TOKEN"

# List all your documents
curl http://127.0.0.1:5000/api/students/{USER_ID}/documents \
  -H "Authorization: Bearer $TOKEN"

# Download specific document
curl -X GET http://127.0.0.1:5000/api/documents/{DOC_ID}/download \
  -H "Authorization: Bearer $TOKEN" \
  --output offer_letter.pdf
```

---

## Test 7: Submit Assignment (Week 1)

### Create a test PDF

```bash
# On Windows, create a simple text file and convert to PDF
# Or use an existing PDF from your system

# Save path
export PDF_FILE="path/to/your/assignment.pdf"
```

### Submit Assignment

```bash
curl -X POST http://127.0.0.1:5000/api/submissions \
  -H "Authorization: Bearer $TOKEN" \
  -F "application_id=$APP_ID" \
  -F "week_number=1" \
  -F "file=@$PDF_FILE"
```

**Expected Response:**
```json
{
  "message": "Week 1 assignment uploaded, evaluated & graded: 8/10 (A)!",
  "submission": {
    "id": "sub-uuid",
    "application_id": "$APP_ID",
    "week_number": 1,
    "status": "approved",
    "marks": 8,
    "max_marks": 10,
    "feedback": "Good work on the deliverables..."
  }
}
```

---

## Test 8: Submit Remaining Assignments (Weeks 2-4)

Repeat Test 7 for weeks 2, 3, and 4:

```bash
for week in 2 3 4; do
  curl -X POST http://127.0.0.1:5000/api/submissions \
    -H "Authorization: Bearer $TOKEN" \
    -F "application_id=$APP_ID" \
    -F "week_number=$week" \
    -F "file=@$PDF_FILE"
done
```

**After 4 assignments are submitted:**
- Application `completion_status` changes to "eligible"
- Student becomes eligible for certificate

---

## Test 9: Check Certificate Eligibility

```bash
curl http://127.0.0.1:5000/api/payments/certificate/status/$APP_ID \
  -H "Authorization: Bearer $TOKEN"
```

**Response (after 4 assignments):**
```json
{
  "enrollment_id": "$APP_ID",
  "completion_status": "eligible",
  "certificate_id": "WI-CERT-2026-XXXXX",
  "is_paid": false,
  "certificate_fee_inr": 199,
  "status": "READY_FOR_PAYMENT"
}
```

---

## Test 10: Simulate Payment (For Local Testing Only)

### Option A: Use Test Razorpay Credentials
(See RAZORPAY_TESTING.md for setup)

### Option B: Bypass Payment (Dev Mode - Testing Only)

Modify `routes/payment_routes.py` temporarily:

```python
# Find the verify_payment() function and add at the start:
if os.getenv('FLASK_ENV') == 'development':
    # Auto-approve payments in dev mode
    is_valid = True
```

Then create a mock payment:

```bash
# Create order
curl -X POST http://127.0.0.1:5000/api/payments/create-order \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "enrollment_id": "$APP_ID"
  }'

# Response will have order_id starting with "order_mock_"
# Copy it and use for verification
export ORDER_ID="order_mock_XXXXX"

# Verify payment (will auto-pass in dev mode)
curl -X POST http://127.0.0.1:5000/api/payments/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "razorpay_order_id": "$ORDER_ID",
    "razorpay_payment_id": "pay_mock_12345",
    "razorpay_signature": "mock_signature"
  }'
```

---

## Test 11: Access Certificate After Payment

```bash
# Get certificate PDF (should work after payment + 4 assignments)
curl -X GET http://127.0.0.1:5000/api/certificates/{CERT_ID}/pdf \
  -H "Authorization: Bearer $TOKEN" \
  --output certificate.pdf

# Or check via public verification endpoint
curl http://127.0.0.1:5000/api/verify/{CERT_ID}
```

**Expected Response:**
```json
{
  "status": "VERIFIED",
  "certificate_id": "WI-CERT-2026-XXXXX",
  "student_name": "Test Student",
  "internship_title": "Python Development Internship",
  "company_name": "Web Intern Platform",
  "issue_date": "December 14, 2024"
}
```

---

## Complete Test Flow Summary

```bash
# 1. Register User
POST /api/auth/register

# 2. Get Token & User
GET /api/auth/me

# 3. Browse Internships
GET /api/internships

# 4. Apply for Internship
POST /api/applications

# 5. Get Offer Letter
GET /api/documents/{DOC_ID}/download

# 6. Submit Assignment Week 1-4
POST /api/submissions (x4)

# 7. Check Payment Status
GET /api/payments/certificate/status/{APP_ID}

# 8. Create Payment Order
POST /api/payments/create-order

# 9. Verify Payment
POST /api/payments/verify

# 10. Download Certificate
GET /api/certificates/{CERT_ID}/pdf

# 11. Public Verification
GET /api/verify/{CERT_ID}
```

---

## Database Inspection

### View All Data Locally

```bash
# Open database
sqlite3 webintern/webintern.db

# View tables
.tables

# Check applications
SELECT * FROM applications;

# Check submissions
SELECT * FROM submissions;

# Check documents
SELECT * FROM documents;

# Check payments
SELECT * FROM payments;

# Check certificates
SELECT * FROM certificates;

# Exit
.exit
```

---

## Logs & Debugging

### Check Server Output

The Flask server shows debug info in the terminal. Look for:

```
[Info] User authenticated: user-id
[Error] Payment verification failed
[Success] Certificate generated
```

### Enable Debug Logging

Add to code temporarily:

```python
print(f"[DEBUG] Payment status: {is_paid}")
print(f"[DEBUG] Completion status: {app_rec['completion_status']}")
```

---

## Common Issues & Fixes

### Issue: "Unauthorized" Error
**Fix**: Check token is valid and included in Authorization header

### Issue: "Application not found"
**Fix**: Make sure you used the APP_ID from the create_application response

### Issue: "Profile incomplete"
**Fix**: Call /api/auth/complete-profile with all required fields

### Issue: "Payment not verified"
**Fix**: Check RAZORPAY credentials or use dev mode bypass

### Issue: "Certificate not released"
**Fix**: Ensure 4 assignments are submitted AND payment verified

---

## Next Steps

After testing all endpoints:

1. ✅ Frontend integration with these APIs
2. ✅ User profile completion form
3. ✅ Internship browsing UI
4. ✅ Application submission form
5. ✅ Assignment upload interface
6. ✅ Payment integration (Razorpay checkout)
7. ✅ Certificate download UI

All backend functionality is now verified and working!
