# IndexedDB Persistent Storage Implementation Guide

## Overview
This document describes the client-side persistent storage solution implemented for the Internship.com platform using IndexedDB.

**CRITICAL LIMITATION**: All data is tied to the current browser/device storage and will NOT sync across:
- Another phone
- Another computer
- Another browser
- Cleared browser/app storage
- An uninstalled Android app

This is purely local, account-scoped persistence for offline access and data recovery.

---

## Architecture

### 1. Storage Layer (`storage.js`)
Central module for all IndexedDB operations. Provides reusable functions for:
- User account management
- Enrollment persistence
- Offer letter storage
- Certificate storage
- Activity tracking
- Progress monitoring
- Document storage

### 2. Database Structure
**Database Name**: `InternshipComLocalDB`
**Version**: 1

**Object Stores**:
- `users` - User account records (keyPath: `userId`)
- `profiles` - Extended profile data (keyPath: `id`, index: `userId`)
- `enrollments` - Internship enrollments (keyPath: `id`, indexes: `userId`, `userInternship`)
- `applications` - Internship applications (keyPath: `id`, indexes: `userId`, `internshipId`)
- `offerLetters` - Offer letter records (keyPath: `id`, indexes: `userId`, `enrollmentId`)
- `certificates` - Certificate records (keyPath: `id`, indexes: `userId`, `enrollmentId`)
- `activities` - User activities and submissions (keyPath: `id`, indexes: `userId`, `enrollmentId`)
- `progress` - Progress tracking (keyPath: `id`, indexes: `userId`, `enrollmentId`)
- `documents` - Document storage (keyPath: `id`, indexes: `userId`, `type`)
- `session` - Session metadata only (keyPath: `key`)

### 3. Account Scoping
Every record is scoped to a specific user via `userId`:
```javascript
{
  id: "enrollment_123",
  userId: "user_abc123",  // <- Ties record to specific account
  internshipId: "internship_001",
  internshipTitle: "Software Development Internship",
  status: "enrolled",
  enrolledAt: "2026-09-13T10:30:00.000Z"
}
```

---

## How It Works

### Registration/Account Creation
1. User creates account via `/api/auth/register`
2. Server returns user object with `id`
3. Frontend calls `API.setCurrentUser(user)`
4. This automatically calls `Storage.saveUser()` to persist in IndexedDB
5. User record is now tied to this browser/device

### Login Flow
1. User logs in via `/api/auth/login`
2. Server returns user object
3. Frontend calls `API.setCurrentUser(user)` → saves to IndexedDB
4. Frontend calls `Storage.restoreUserAccount(userId)` → loads all account data
5. Dashboard renders with both server and persisted data

### Enrollment/Application
1. User clicks "Apply" for an internship
2. POST request sent to `/api/applications`
3. On success, frontend saves to IndexedDB via `Storage.saveEnrollment()`
4. Enrollment is now persistent locally
5. Dashboard can display this even when offline

### Logout
**CRITICAL**: Logout only clears session tokens, NOT persistent data
```javascript
API.setAuthToken(null);      // Clear session
API.setCurrentUser(null);    // Clear current user
// IndexedDB data remains untouched
```

### Login Again
1. User logs in with credentials
2. Server authenticates and returns user
3. `Storage.restoreUserAccount(userId)` loads all stored data
4. All previous enrollments, certificates, offer letters are restored

---

## Key Functions

### User Management
```javascript
await Storage.saveUser(user)              // Save user account
await Storage.getUser(userId)             // Get user by ID
await Storage.getUserByEmail(email)       // Get user by email
await Storage.deleteUser(userId)          // Delete user (only on explicit account deletion)
```

### Enrollment Management
```javascript
await Storage.saveEnrollment(enrollment)           // Save enrollment
await Storage.getEnrollment(enrollmentId)          // Get single enrollment
await Storage.getUserEnrollments(userId)           // Get all user's enrollments
await Storage.getEnrollmentByInternship(userId, internshipId) // Prevent duplicates
await Storage.deleteEnrollment(enrollmentId)       // Remove enrollment
```

### Offer Letters
```javascript
await Storage.saveOfferLetter(offerLetter)     // Save offer letter
await Storage.getOfferLetter(offerId)          // Get offer letter
await Storage.getUserOfferLetters(userId)      // Get all user's offers
```

### Certificates
```javascript
await Storage.saveCertificate(certificate)     // Save certificate
await Storage.getCertificate(certId)           // Get certificate
await Storage.getUserCertificates(userId)      // Get all user's certificates
```

### Account Restoration
```javascript
const accountData = await Storage.restoreUserAccount(userId);
// Returns: { profile, enrollments, applications, offerLetters, certificates, activities }
```

---

## Prevent Cross-Account Data Leaks

Every read operation is filtered by `userId`:

**WRONG** (would leak data):
```javascript
const allEnrollments = enrollments.getAll();
```

**RIGHT** (properly scoped):
```javascript
const userEnrollments = await Storage.getUserEnrollments(currentUserId);
```

The dashboard uses:
```javascript
const user = API.getCurrentUser();
const enrollments = await Storage.getUserEnrollments(user.id);
// Only this user's data is loaded
```

---

## Session vs. Persistent Data

### Session Data (Cleared on Logout)
- `access_token` in localStorage
- `user_profile` in localStorage
- These are cleared when user clicks "Sign Out"

### Persistent Account Data (NOT Cleared on Logout)
- Enrollments in IndexedDB
- Certificates in IndexedDB
- Offer letters in IndexedDB
- Profile information in IndexedDB
- Progress data in IndexedDB
- Activity history in IndexedDB

**Why**: User's data should survive logout/login cycles, but session tokens should not.

---

## Testing the Implementation

### Test Case 1: Account Creation & Persistence
1. Create new account with email, name, phone, college, department
2. Verify account appears in IndexedDB `users` store
3. Logout and login again
4. Verify profile data is restored

### Test Case 2: Enrollment Persistence
1. Login
2. Enroll in Internship A
3. Verify enrollment saved to IndexedDB `enrollments` store
4. Refresh page → enrollment still visible
5. Logout and login again → enrollment still visible
6. Close and reopen browser → enrollment still visible

### Test Case 3: Offer Letter Persistence
1. Enroll in internship (generates offer letter)
2. Verify offer letter saved to IndexedDB `offerLetters` store
3. Logout → login → offer letter still accessible
4. Refresh page → offer letter still accessible

### Test Case 4: Certificate Persistence
1. Complete internship and generate certificate
2. Verify certificate saved to IndexedDB `certificates` store
3. Logout → login → certificate still available
4. Close and reopen browser → certificate still available

### Test Case 5: Cross-Account Isolation
1. Create/Login Account A
2. Enroll in Internship A
3. Logout
4. Create/Login Account B
5. Verify Account A's data is NOT visible
6. Enroll in Internship B
7. Logout → Login Account A → Only Internship A visible (not B)
8. Logout → Login Account B → Only Internship B visible (not A)

### Test Case 6: Multiple Accounts on Same Device
1. Account A enrolls in Internship A1 and A2
2. Logout
3. Account B enrolls in Internship B1
4. Logout → Login Account A → Both A1 and A2 visible, B1 NOT visible
5. Logout → Login Account B → B1 visible, A1 and A2 NOT visible

### Test Case 7: Offline Access
1. Login and enroll in internship
2. Disconnect internet
3. Refresh page
4. Enrollment still visible (from IndexedDB)
5. Reconnect and sync with server

---

## Data Durability

### Data Survives
✅ Page refresh
✅ Browser restart
✅ PWA restart
✅ Android app restart (PWA)
✅ Logout/login cycles
✅ Offline navigation
✅ Switching between different app sections

### Data Does NOT Survive
❌ Clearing browser cache/storage
❌ Uninstalling app (on Android)
❌ Logging in from a different browser
❌ Logging in from a different device
❌ Browser profile deletion
❌ Private/Incognito mode (uses separate storage)

---

## Storage Limitations

### IndexedDB Size Limits
- Typical: 50MB per origin (most browsers)
- Chrome/Edge: Up to 10% of available disk space
- Firefox: Up to 10% of available disk space
- Safari: 50MB per origin

For this internship platform:
- User record: ~1KB
- Enrollment record: ~2KB
- Certificate record: ~5KB
- ~100 enrollments + certificates = <1MB

**Plenty of space available**

---

## Error Handling

All storage operations include try-catch:

```javascript
try {
  await Storage.saveEnrollment(enrollment);
  console.log('[Storage] Enrollment saved');
} catch (error) {
  console.warn('[Storage] Failed to save enrollment:', error);
  // Gracefully degrade - app continues working
}
```

If IndexedDB fails:
- App continues working with server data only
- No data loss on server side
- User can still complete their internship

---

## Migration & Data Versioning

### Current Version
- `DB_VERSION: 1`
- Schema includes all necessary stores for internship platform

### Future Migrations
To add new stores or modify schema:
```javascript
// In storage.js, increment DB_VERSION
DB_VERSION: 2

// In onupgradeneeded handler, add new stores
if (!db.objectStoreNames.contains('newStore')) {
  db.createObjectStore('newStore', { keyPath: 'id' });
}
```

Migration happens automatically on next page load.

---

## Implementation Checklist

- [x] Created `storage.js` with IndexedDB layer
- [x] Updated `api.js` to save user data on login
- [x] Updated `authViews.js` to restore account data after login
- [x] Updated `dashboardView.js` to load persistent data
- [x] Updated `detailView.js` to save enrollments on apply
- [x] Updated `header.js` logout to NOT clear persistent data
- [x] Added `storage.js` to HTML script tags
- [x] Verified account scoping with userId
- [x] Tested cross-account isolation
- [x] Tested persistence across logout/login

---

## Technical Notes

### Why IndexedDB vs. localStorage
- **localStorage**: ~5-10MB limit, synchronous (blocks UI), stored as JSON strings
- **IndexedDB**: 50MB+, asynchronous (non-blocking), supports binary data, proper transactions

### Why Not Use External Database
- **Requirement**: No external services (Firebase, Supabase, etc.)
- **Trade-off**: Data doesn't sync across devices, but fully offline-capable
- **Benefit**: No backend dependency for offline functionality

### Why Not Use SQLite (Web)
- SQLite.js requires compilation and adds 3-4MB to bundle
- IndexedDB is native browser API
- IndexedDB is sufficient for this use case

---

## Troubleshooting

### "IndexedDB not available"
- Check browser compatibility (IE11 not supported)
- Check if user is in Private/Incognito mode
- Check browser's storage permissions

### Data not persisting
- Verify `Storage.init()` was called
- Check browser console for errors
- Verify `userId` is being set correctly
- Check IndexedDB quota not exceeded

### Cross-account data leaking
- Always filter by `userId` in reads
- Never display global arrays without filtering
- Use `Storage.getUserEnrollments(userId)` not `getAll()`

---

## Support & Maintenance

For issues or questions:
1. Check browser console for [Storage] errors
2. Verify IndexedDB is available
3. Check that userId is consistent
4. Verify network requests are working
5. Try clearing cache and logging in again
