# Razorpay Payment Testing Guide

## Problem: Razorpay popup opens but payment fails

This happens because either:
1. **No Razorpay credentials** - Test keys not configured
2. **Invalid payment amount** - Amount mismatch
3. **Signature verification failed** - Key mismatch between frontend and backend

---

## Solution: Setup Razorpay Test Mode

### Step 1: Create Razorpay Account

1. Go to https://razorpay.com
2. Sign up for a free account
3. Verify your email
4. Complete KYC (identity verification)

### Step 2: Get Test API Keys

1. Login to https://dashboard.razorpay.com
2. Click on **Settings** → **API Keys**
3. Copy your **TEST Mode keys**:
   - `Key ID` (e.g., `rzp_test_XXXXXXXXXXXXXXXX`)
   - `Key Secret` (e.g., `XXXXXXXXXXXXXXXXXXXXX`)
4. Also note the **Webhook Secret** (if webhook testing needed)

### Step 3: Update .env File

Edit `webintern/.env` and replace:

```env
RAZORPAY_KEY_ID=rzp_test_XXXXXXXXXXXXXXXX
RAZORPAY_KEY_SECRET=your_test_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
```

### Step 4: Restart Backend

```bash
# Stop current server (Ctrl+C)
# Then restart:
python webintern/app.py
```

---

## Test Payment Flow

### Using Razorpay Test Cards

After setup, use these test card details in the Razorpay popup:

**Success Payment:**
- Card Number: `4111 1111 1111 1111`
- Expiry: Any future date (e.g., 12/25)
- CVV: Any 3 digits (e.g., 123)
- Name: Any name

**Failed Payment (to test error handling):**
- Card Number: `4000 0000 0000 0002`
- Expiry: Any future date
- CVV: Any 3 digits

### Expected Behavior

1. Click "Pay Now" button
2. Razorpay popup opens
3. Enter test card details
4. Click "Pay" 
5. **Success**: Certificate should be generated and emailed
6. **Failure**: Error message appears

---

## Verification

### Check Payment Status

```bash
# Via API
GET http://127.0.0.1:5000/api/payments/certificate/status/{enrollment_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "enrollment_id": "...",
  "completion_status": "pending",
  "certificate_id": "WI-CERT-2026-XXXXX",
  "is_paid": true,
  "certificate_fee_inr": 199,
  "status": "READY_FOR_PAYMENT" or "PAYMENT_PAID"
}
```

### Check Database

```bash
# View payments
sqlite3 webintern/webintern.db "SELECT * FROM payments LIMIT 5;"

# View certificates
sqlite3 webintern/webintern.db "SELECT * FROM certificates LIMIT 5;"
```

---

## Troubleshooting

### Issue 1: "Invalid Key Id" Error

**Cause:** Razorpay credentials not set or incorrect

**Fix:**
```bash
# Verify .env file exists
ls webintern/.env

# Check it has valid keys
grep RAZORPAY webintern/.env
```

### Issue 2: "Signature Verification Failed"

**Cause:** Key mismatch or order ID not created properly

**Fix:**
1. Ensure `RAZORPAY_KEY_SECRET` matches exactly (copy-paste again)
2. Restart backend: `python webintern/app.py`
3. Try payment again

### Issue 3: Popup Shows But No Payment Button

**Cause:** Frontend Razorpay script not loaded

**Fix:**
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Verify frontend is calling `/api/payments/create-order` correctly

---

## Advanced: Mock Testing (No Razorpay Account)

If you want to test WITHOUT Razorpay credentials:

### Option A: Modify Backend to Auto-Complete Payments

Edit `routes/payment_routes.py`:

```python
# In verify_payment() function, add:
if razorpay_order_id.startswith("order_mock_"):
    # Auto-verify mock payments for local testing
    is_valid = True
```

Then in frontend, manually call payment verification after creating order.

### Option B: Bypass Payment for Testing

In `routes/certificate_routes.py`, change payment gate:

```python
# Temporarily disable for testing
if not is_paid and os.getenv('FLASK_ENV') == 'development':
    is_paid = True  # Auto-pass payment gate in dev mode
```

⚠️ **WARNING**: Only use for local testing. Remove before production.

---

## Production Setup

When deploying to production:

1. Switch to **Live Keys** in Razorpay Dashboard
2. Update `.env` with Live Key ID and Secret:
   ```env
   RAZORPAY_KEY_ID=rzp_live_XXXXXXXXXXXXXXXX
   RAZORPAY_KEY_SECRET=your_live_key_secret
   ```
3. Update `APP_URL` to production domain:
   ```env
   APP_URL=https://yourdomain.com
   ```
4. Set `FLASK_ENV=production`
5. Deploy

---

## Support

- Razorpay Docs: https://razorpay.com/docs/
- Razorpay Support: support@razorpay.com
- Test Mode Expires: Never (test keys are permanent)

---

## Summary

✅ Create Razorpay account  
✅ Get TEST API keys  
✅ Add keys to `.env`  
✅ Restart backend  
✅ Try payment with test card  
✅ Verify payment recorded in database  

Once this works, certificate will auto-generate and email when 4 assignments are completed.
