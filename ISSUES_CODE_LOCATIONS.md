# Desktop vs Mobile Issues - Exact Code Locations & Fixes

## 🔴 CRITICAL ISSUES (Must Fix Now)

---

### 1. PAYMENT SIGNATURE VERIFICATION STUB (SECURITY HOLE)

**Location**: `routes/payment_routes.py` (Check this file)

**What to Look For**:
```python
# Line ~65: Payment verification endpoint
razorpay_signature: 'simulated_signature'  # ❌ HARDCODED FAKE VALUE
```

**Issue**: Anyone can claim payment without paying. Complete security bypass.

**Fix Required**: Replace with actual Razorpay signature validation
```python
# CORRECT implementation:
import hmac
import hashlib

def verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    # Create signature string
    body = razorpay_order_id + '|' + razorpay_payment_id
    
    # Calculate expected signature
    expected_signature = hmac.new(
        Config.RAZORPAY_SECRET.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Compare
    if expected_signature != razorpay_signature:
        return False
    return True

# Use in payment verify endpoint:
if not verify_razorpay_signature(order_id, payment_id, signature):
    return jsonify({'error': 'Invalid payment signature'}), 403
```

**Severity**: 🔴 CRITICAL - Revenue loss risk

---

### 2. MOBILE MODAL OVERLAPS BOTTOM NAVIGATION BAR

**Location**: Multiple files
- `static/js/views/dashboardView.js` - modal for workspace
- `static/js/views/detailView.js` - apply button in sticky card
- `static/css/main.css` or `components.css` - modal CSS

**What to Look For**:
```css
/* In CSS files */
.modal-card {
  position: fixed;
  max-height: 90vh;
  bottom: 0;
  z-index: 200;
  /* ❌ NO padding for bottom bar! */
}

/* In JS modals */
const modal = document.createElement('div');
modal.style.maxHeight = '90vh';  /* ❌ Doesn't account for --bottom-bar-height */
```

**Issue**: On mobile, modal content hidden behind bottom navigation (60px high)

**Examples**:
1. **Detail View Modal**: Apply button unreachable
2. **Dashboard Workspace Modal**: Upload form hidden

**Fix Required**:

```css
/* Add to mobile-app.css or main.css */
@media (max-width: 768px) {
  .modal-card {
    max-height: calc(100vh - var(--bottom-bar-height) - 40px);
    /* Account for bottom bar (60px) + padding (40px) */
    bottom: calc(var(--bottom-bar-height) + 20px);
    padding-bottom: env(safe-area-inset-bottom);
  }
  
  /* All fixed-position modals */
  .modal-backdrop {
    bottom: 0;
    height: calc(100vh - var(--bottom-bar-height));
  }
}

/* In JS when creating modals */
modal.style.maxHeight = `calc(100vh - ${bottomBarHeight}px - 40px)`;
modal.style.bottom = `${bottomBarHeight}px`;
```

**Check These Files**:
- Search for `.modal-card` in all CSS files
- Search for `max-height: 90vh` in all JS view files
- Search for `position: fixed` modals

**Severity**: 🔴 CRITICAL - Mobile app unusable for key features

---

### 3. DATA RACE: ENROLLMENT DOESN'T SYNC TO OTHER DEVICE

**Location**: Multiple files
- `routes/application_routes.py` (lines 190-200) - enrollment creation
- `static/js/views/detailView.js` (lines 130-150) - apply button handler
- `utils/supabase_client.py` - sync logic

**Problem Flow**:
```
1. Mobile user enrolls
   → POST /api/applications
   → Saves to SQLite (immediate)
   → Starts Supabase sync (async, 5+ seconds on 3G)
   
2. JavaScript waits 2 seconds
   setTimeout(() => window.location.hash = '#/dashboard', 2000)
   
3. Dashboard loads
   → GET /api/applications/me
   → Queries SQLite (Supabase sync NOT finished!)
   → Returns empty for new enrollment
   
4. User sees: "No active internships"
5. Desktop user sees: Mobile's enrollment missing

❌ PROBLEM: 2-second delay is shorter than actual sync time
```

**What to Look For**:

In `static/js/views/detailView.js`:
```javascript
// ❌ CURRENT CODE (WRONG):
setTimeout(() => {
  window.location.hash = '#/dashboard';
}, 2000);  // Too short! Sync might not complete
```

In `routes/application_routes.py`:
```python
# Line ~193: Background sync started
sync_application_to_supabase_async(...)  # Takes 2-10 seconds
# But frontend doesn't wait for this!
```

**Fix Required**: Wait for actual enrollment to appear

Option 1 - Poll until found:
```javascript
// static/js/views/detailView.js
async function waitForEnrollmentSync(appId, maxWait = 10000) {
  const startTime = Date.now();
  while (Date.now() - startTime < maxWait) {
    const apps = await API.getMyApplications();
    if (apps.applications.some(a => a.id === appId)) {
      return true;  // Enrollment synced!
    }
    await new Promise(r => setTimeout(r, 500));  // Poll every 500ms
  }
  return false;
}

// In apply button handler:
try {
  const res = await API.applyInternship(internship.id);
  statusMsg.innerHTML = `<span style="color: var(--primary);">✅ Syncing enrollment...</span>`;
  
  const synced = await waitForEnrollmentSync(res.application.id);
  if (synced) {
    statusMsg.innerHTML = `<span style="color: var(--success);">✅ Enrolled! Redirecting...</span>`;
  } else {
    statusMsg.innerHTML = `<span style="color: var(--warning);">⚠️ Still syncing, redirecting anyway...</span>`;
  }
  
  setTimeout(() => {
    window.location.hash = '#/dashboard';
  }, 1000);
}
```

Option 2 - Return sync confirmation from backend:
```python
# routes/application_routes.py
def create_application():
    # ... existing code ...
    
    # Wait for Supabase sync to complete before returning
    max_retries = 10
    retry_count = 0
    synced = False
    
    while retry_count < max_retries and not synced:
        try:
            # Check if application exists in Supabase
            resp = requests.get(
                f"{url}/rest/v1/applications?id=eq.{app_id}",
                headers=headers,
                timeout=5
            )
            if resp.status_code == 200 and resp.json():
                synced = True
            else:
                retry_count += 1
                if retry_count < max_retries:
                    import time
                    time.sleep(1)
        except:
            retry_count += 1
            if retry_count < max_retries:
                import time
                time.sleep(1)
    
    return jsonify({
        'message': 'Enrollment successful',
        'application': app_obj,
        'synced': synced  # NEW: Tell frontend if synced
    }), 201

# static/js/api.js - check if synced
async applyInternship(internshipId) {
  const res = await this.request('/api/applications', {
    method: 'POST',
    body: JSON.stringify({ internship_id: internshipId })
  });
  
  if (!res.synced) {
    console.warn('Enrollment not yet synced to Supabase');
    // Wait longer before redirect
    await new Promise(r => setTimeout(r, 3000));
  }
  
  return res;
}
```

**Severity**: 🔴 CRITICAL - Data loss/inconsistency

---

### 4. RAZORPAY PAYMENT TIMEOUT ON MOBILE 3G

**Location**: `static/js/views/dashboardView.js` (certificate payment handler)

**What to Look For**:
```javascript
// ❌ Current code (no timeout handling)
Razorpay.open();  // Just opens modal without checking if script loaded
```

**Problem**: On 3G networks, Razorpay script takes 5+ seconds to load from CDN

**Fix Required**: Add timeout detection and retry

```javascript
// In dashboardView.js or a new payment handler file
async function initiateRazorpayPayment(appId, certId, amount) {
  // Show loading
  const btn = document.querySelector('[data-action="pay"]');
  const originalText = btn.textContent;
  btn.disabled = true;
  btn.textContent = '⏳ Loading payment gateway...';
  
  // Timeout check for Razorpay script
  const scriptLoadTimeout = new Promise((_, reject) => 
    setTimeout(() => reject(new Error('Payment gateway timeout')), 8000)
  );
  
  try {
    // Wait for Razorpay to be ready OR timeout
    await Promise.race([
      new Promise(resolve => {
        if (window.Razorpay) {
          resolve();  // Already loaded
        } else {
          // Load from CDN with timeout
          const script = document.createElement('script');
          script.src = 'https://checkout.razorpay.com/v1/checkout.js';
          script.onload = resolve;
          script.onerror = () => reject(new Error('Failed to load payment gateway'));
          document.head.appendChild(script);
        }
      }),
      scriptLoadTimeout
    ]);
    
    // Create payment order
    const orderRes = await API.createPaymentOrder(certId, appId);
    
    // Open Razorpay
    const options = {
      key: CONFIG.RAZORPAY_KEY,
      amount: amount,
      currency: 'INR',
      order_id: orderRes.order_id,
      prefill: {
        email: userEmail,
        contact: userPhone
      },
      handler: async (response) => {
        // Verify payment
        const verified = await API.verifyPayment(response);
        if (verified) {
          showNotification('Payment successful! Certificate unlocked.', 'success');
        }
      },
      modal: {
        ondismiss: () => {
          btn.disabled = false;
          btn.textContent = originalText;
        }
      }
    };
    
    new window.Razorpay(options).open();
    
  } catch (error) {
    if (error.message.includes('timeout')) {
      showNotification('Payment gateway is loading slowly. Please try again in a moment.', 'warning');
      // Show retry button
      btn.textContent = '🔄 Retry Payment';
      btn.disabled = false;
    } else {
      showNotification(error.message, 'danger');
      btn.disabled = false;
      btn.textContent = originalText;
    }
  }
}
```

**Severity**: 🔴 CRITICAL - Mobile users can't complete payment

---

## 🟠 HIGH PRIORITY ISSUES

---

### 5. STICKY SUMMARY CARD HIDDEN BY BOTTOM BAR

**Location**: `static/js/views/detailView.js` + CSS

**Current Code**:
```html
<!-- Right sidebar with sticky card -->
<div style="position: sticky; top: 80px;">
  <div class="card">
    <!-- Apply button -->
    <button id="apply-now-btn">Apply Now</button>
  </div>
</div>
```

**Problem**: On mobile, button disappears behind 60px bottom bar

**Fix**:
```html
<!-- Update to account for mobile -->
<div id="summary-card" style="position: sticky;">
  <div class="card">
    <button id="apply-now-btn">Apply Now</button>
  </div>
</div>

<style>
@media (max-width: 768px) {
  #summary-card {
    position: sticky;
    top: auto;
    bottom: calc(var(--bottom-bar-height) + 20px);
    margin-bottom: 80px;  /* Space for bottom bar */
  }
}

@media (min-width: 769px) {
  #summary-card {
    position: sticky;
    top: 80px;
  }
}
</style>
```

**Check**: Search for `position: sticky` in `detailView.js`

---

### 6. REFERRAL INPUT TOO WIDE

**Location**: `static/js/views/dashboardView.js` (referral link section)

**Current Code**:
```html
<div style="display: flex; gap: 12px;">
  <input style="flex: 1; min-width: 240px" readonly />
  <!-- ❌ min-width: 240px too wide for 320px phone -->
  <button>Copy</button>
</div>
```

**Fix**:
```html
<div style="display: flex; gap: 12px; min-width: 0;">
  <!-- min-width: 0 allows flex item to shrink below content size -->
  <input style="flex: 1; min-width: 0; width: 100%" readonly />
  <button style="flex-shrink: 0;">Copy</button>
</div>
```

---

### 7. SUPABASE QUERIES TOO SLOW

**Location**: `routes/application_routes.py` lines 200-217 (get_my_applications function)

**Current Code**:
```python
def get_my_applications():
    # Fast: Query local SQLite
    cursor.execute("SELECT ... FROM applications WHERE user_id = ?")
    apps = [dict(r) for r in cursor.fetchall()]
    
    # SLOW: Query Supabase with 10s timeout
    sp_apps = fetch_applications_from_supabase(user_id, user_email)
    # Takes 10+ seconds on slow networks!
    
    # Re-query SQLite if Supabase returned data
    cursor.execute("SELECT ...")
    apps = [dict(r) for r in cursor.fetchall()]
    
    return jsonify({'applications': apps})
```

**Fix**: Return local data immediately, fetch Supabase in background

```python
def get_my_applications():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get local apps immediately
    cursor.execute("""
        SELECT a.*, i.title as internship_title, ...
        FROM applications a
        JOIN internships i ON a.internship_id = i.id
        WHERE a.user_id = ? OR LOWER(a.user_id) = ? OR a.user_id IN (SELECT id FROM profiles WHERE LOWER(email) = ?)
        ORDER BY a.applied_at DESC
    """, (user_id, user_email, user_email))
    apps = [dict(r) for r in cursor.fetchall()]
    
    # Fetch Supabase in background (non-blocking)
    def fetch_and_sync_supabase():
        try:
            from utils.supabase_client import fetch_applications_from_supabase
            sp_apps = fetch_applications_from_supabase(user_id, user_email)
            if sp_apps:
                for sa in sp_apps:
                    # Insert missing enrollments
                    cursor.execute("""
                        INSERT OR IGNORE INTO applications (...)
                        VALUES (...)
                    """, (...))
                conn.commit()
        except Exception as e:
            log_error(f"Supabase sync failed: {e}")
        finally:
            conn.close()
    
    # Start background sync thread with SHORT timeout
    import threading
    t = threading.Thread(target=fetch_and_sync_supabase, daemon=False)
    t.daemon = False
    t.start()
    
    # Return local data immediately
    conn.close()
    return jsonify({'applications': apps}), 200
```

---

### 8. NO NETWORK DETECTION

**Location**: `static/js/api.js`

**Add**:
```javascript
// At top of api.js
export const NetworkMonitor = {
  isOnline: navigator.onLine,
  
  init() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.onOnline?.();
    });
    
    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.onOffline?.();
    });
  },
  
  onOnline: null,
  onOffline: null
};

// In app.js init:
NetworkMonitor.init();
NetworkMonitor.onOffline = () => {
  showNotification('No internet connection', 'warning');
};
NetworkMonitor.onOnline = () => {
  showNotification('Connection restored', 'success');
  // Retry failed requests
};

// Before API calls:
if (!NetworkMonitor.isOnline) {
  throw new Error('No internet connection');
}
```

---

### 9. COPY TO CLIPBOARD FAILS ON OLD PHONES

**Location**: `static/js/views/dashboardView.js` (referral copy button)

**Current**:
```javascript
button.addEventListener('click', async () => {
  await navigator.clipboard.writeText(referralLink);
  // ❌ Fails on iOS < 13.3, old Android
});
```

**Fix**:
```javascript
async function copyToClipboard(text) {
  // Try modern API first
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (e) {
      console.warn('Clipboard API failed, using fallback');
    }
  }
  
  // Fallback for older browsers
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  textarea.style.pointerEvents = 'none';
  document.body.appendChild(textarea);
  
  try {
    textarea.select();
    textarea.setSelectionRange(0, text.length);  // For iOS
    const success = document.execCommand('copy');
    return success;
  } finally {
    document.body.removeChild(textarea);
  }
}

// Use it:
const btn = document.querySelector('.copy-referral-btn');
btn.addEventListener('click', async () => {
  const copied = await copyToClipboard(referralLink);
  if (copied) {
    showNotification('Link copied!', 'success');
  } else {
    showNotification('Copy failed, try selecting text manually', 'warning');
  }
});
```

---

### 10. TABLE TEXT UNREADABLE ON MOBILE

**Location**: `static/js/views/dashboardView.js` (referred friends table)

**Current**:
```css
table {
  font-size: 0.9rem;  /* 14px - too small */
  padding: 12px;
}
```

**Fix**:
```css
@media (max-width: 768px) {
  table {
    font-size: 1rem;  /* 16px for readability */
    padding: 8px;
  }
  
  tbody tr {
    border-bottom: 1px solid #e2e8f0;
    display: block;
    padding: 12px 0;
  }
  
  tbody td {
    display: grid;
    grid-template-columns: 120px 1fr;
    gap: 8px;
    padding: 4px 8px;
  }
  
  tbody td::before {
    content: attr(data-label);
    font-weight: 600;
    color: var(--text-muted);
  }
}
```

**And update HTML**:
```html
<td data-label="Name">Friend Name</td>
<td data-label="Status">Enrolled</td>
```

---

### 11. TOKEN EXPIRY NOT HANDLED

**Location**: `static/js/api.js` (request function)

**Current**:
```javascript
async request(endpoint, options = {}) {
  const response = await fetch(url, config);
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.error);  // ❌ Doesn't check for 401
  }
  return data;
}
```

**Fix**:
```javascript
async request(endpoint, options = {}) {
  const response = await fetch(url, config);
  const data = await response.json();
  
  // Check for token expiry
  if (response.status === 401) {
    this.clearToken();
    window.location.hash = '#/login';
    throw new Error('Session expired. Please login again.');
  }
  
  if (!response.ok) {
    throw new Error(data.error || `Error ${response.status}`);
  }
  
  return data;
}
```

---

## Summary of Code Locations

| Issue | File | Line/Search |
|-------|------|------------|
| Payment signature | `routes/payment_routes.py` | Search: `simulated_signature` |
| Modal overlap | `static/css/mobile-app.css` | Search: `.modal-card` |
| Modal overlap | Multiple JS views | Search: `max-height: 90vh` |
| Data race | `static/js/views/detailView.js` | Line ~145 `setTimeout` |
| Data race | `routes/application_routes.py` | Line ~193 `sync_application_to_supabase_async` |
| Razorpay timeout | `static/js/views/dashboardView.js` | Search: `Razorpay.open()` |
| Sticky card | `static/js/views/detailView.js` | Search: `position: sticky` |
| Referral input | `static/js/views/dashboardView.js` | Search: `min-width: 240px` |
| Supabase slow | `routes/application_routes.py` | Line ~200-217 `get_my_applications` |
| No network | `static/js/api.js` | Add network event listener |
| Copy clipboard | `static/js/views/dashboardView.js` | Search: `navigator.clipboard` |
| Table readable | `static/css/components.css` | Search: `table` |
| Token expiry | `static/js/api.js` | In `request()` function |

---

## Testing Checklist After Fixes

- [ ] Test payment on slow 3G network
- [ ] Test enrollment on mobile, check appears on desktop
- [ ] Test desktop enrollment, check appears on mobile
- [ ] Test modal opens properly on mobile, apply button visible
- [ ] Test referral link copy on iPhone SE (320px)
- [ ] Test dashboard loads in < 2 seconds on 3G
- [ ] Test table readable on iPhone 8 (375px)
- [ ] Test offline mode - shows warning, retries on reconnect
- [ ] Test token expiry - shows login prompt
- [ ] Test on devices: iPhone SE, Galaxy S21, iPad

