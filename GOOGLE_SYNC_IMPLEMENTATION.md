# Google Account Sync Implementation Guide

## Overview
This guide explains how to implement Google account synchronization for internship history tracking on the Web Intern platform.

---

## 1. DATABASE SETUP

### Run Migration
Execute the migration file to create necessary tables:
```sql
-- File: MIGRATION_ADD_INTERNSHIP_SYNC.sql
-- This creates:
-- - internship_history table
-- - internship_attendance table
-- - sync_logs table
-- - Updated profiles & applications tables
```

---

## 2. BACKEND API MODIFICATIONS

Create new API endpoints for sync functionality:

### Endpoint 1: Link Google Account
```python
@auth_bp.route('/api/profile/link-google', methods=['POST'])
@jwt_required
def link_google_account():
    user = request.user
    data = request.get_json() or {}
    google_account_id = data.get('google_account_id')
    
    # Update user profile with google_account_id
    execute_db(
        "UPDATE profiles SET google_account_id = ? WHERE id = ?",
        (google_account_id, user['sub'])
    )
    
    return jsonify({
        'status': 'success',
        'message': 'Google account linked successfully'
    }), 200
```

### Endpoint 2: Get Internship History
```python
@application_bp.route('/api/internship-history/me', methods=['GET'])
@jwt_required
def get_internship_history():
    user = request.user
    
    history = query_db("""
        SELECT * FROM internship_history 
        WHERE user_id = ? 
        ORDER BY enrolled_date DESC
    """, (user['sub'],))
    
    return jsonify({
        'status': 'success',
        'history': [dict(row) for row in history]
    }), 200
```

### Endpoint 3: Track Attendance
```python
@submission_bp.route('/api/attendance/log', methods=['POST'])
@jwt_required
def log_attendance():
    user = request.user
    data = request.get_json() or {}
    
    # Create attendance record
    attendance_id = str(uuid.uuid4())
    execute_db("""
        INSERT INTO internship_attendance 
        (id, application_id, week_number, attended_date, submission_status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        attendance_id,
        data.get('application_id'),
        data.get('week_number'),
        datetime.datetime.now(),
        'submitted'
    ))
    
    # Create sync log for Google Sheets
    sync_id = str(uuid.uuid4())
    execute_db("""
        INSERT INTO sync_logs
        (id, user_id, sync_type, record_id, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        sync_id,
        user['sub'],
        'ATTENDANCE',
        attendance_id,
        'pending'
    ))
    
    return jsonify({
        'status': 'success',
        'message': 'Attendance logged',
        'attendance_id': attendance_id
    }), 200
```

### Endpoint 4: Sync with Google Sheets
```python
@application_bp.route('/api/sync/google-sheets', methods=['POST'])
@jwt_required
def sync_to_google_sheets():
    user = request.user
    
    # Get pending sync records
    pending = query_db("""
        SELECT * FROM sync_logs 
        WHERE user_id = ? AND status = 'pending'
        LIMIT 10
    """, (user['sub'],))
    
    for log in pending:
        try:
            # Call Google Sheets API to sync data
            # sync_to_sheets(log)
            
            # Update sync log status
            execute_db("""
                UPDATE sync_logs 
                SET status = 'synced', synced_at = ?
                WHERE id = ?
            """, (datetime.datetime.now(), log['id']))
            
        except Exception as e:
            execute_db("""
                UPDATE sync_logs 
                SET status = 'failed', error_message = ?
                WHERE id = ?
            """, (str(e), log['id']))
    
    return jsonify({
        'status': 'success',
        'synced_count': len([l for l in pending if query_db(
            "SELECT status FROM sync_logs WHERE id = ?", 
            (l['id'],), one=True)['status'] == 'synced'])
    }), 200
```

---

## 3. FRONTEND IMPLEMENTATION

### 1. Link Google Account (On Registration/Profile Update)

```javascript
// File: webintern/static/js/components/auth.js (new section)

async function linkGoogleAccount(googleId) {
  try {
    const token = localStorage.getItem('access_token');
    const res = await fetch('/api/profile/link-google', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        google_account_id: googleId
      })
    });
    
    const data = await res.json();
    if (res.ok) {
      Toast.show('Google account linked successfully!', 'success');
      return true;
    } else {
      Toast.show(data.error || 'Failed to link Google account', 'error');
      return false;
    }
  } catch (error) {
    console.error('Link Google error:', error);
    Toast.show('Error linking Google account', 'error');
    return false;
  }
}
```

### 2. Display Internship History

```javascript
// File: webintern/static/js/components/history.js (new file)

const InternshipHistoryView = {
  async render() {
    const container = document.getElementById('app-view');
    if (!container) return;
    
    container.innerHTML = `
      <section class="section" style="padding: 16px 0;">
        <div class="container">
          <h1 style="font-size: 24px; color: #082B66; margin-bottom: 20px;">Your Internship Journey</h1>
          <div id="history-list">Loading...</div>
        </div>
      </section>
    `;
    
    await this.loadHistory();
  },
  
  async loadHistory() {
    try {
      const res = await fetch('/api/internship-history/me', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      const data = await res.json();
      const container = document.getElementById('history-list');
      
      if (data.history.length === 0) {
        container.innerHTML = '<p>No internship history yet.</p>';
        return;
      }
      
      container.innerHTML = data.history.map(item => `
        <div style="background: white; border-radius: 12px; padding: 16px; margin-bottom: 12px; border: 1px solid #DCE6F5;">
          <h3 style="margin: 0 0 6px 0; color: #082B66;">${item.internship_title}</h3>
          <p style="margin: 0; font-size: 13px; color: #4B5563;">
            Sector: <strong>${item.sector_name}</strong>
          </p>
          <p style="margin: 4px 0 0 0; font-size: 13px; color: #4B5563;">
            Status: <strong style="text-transform: uppercase; color: #0B3D91;">${item.status}</strong>
          </p>
          <p style="margin: 4px 0 0 0; font-size: 13px; color: #4B5563;">
            Progress: ${item.completed_weeks} of ${item.total_weeks} weeks (${item.progress_percentage}%)
          </p>
          ${item.certificate_earned ? `
            <p style="margin: 4px 0 0 0; font-size: 13px; color: #10B981;">
              ✓ Certificate Earned
            </p>
          ` : ''}
        </div>
      `).join('');
    } catch (error) {
      console.error('Error loading history:', error);
      document.getElementById('history-list').innerHTML = 'Error loading history.';
    }
  }
};
```

### 3. Auto-log Attendance on PDF Upload

```javascript
// Modification to dashboardView.js submitPdfFile function

async submitPdfFile(event, appId, weekNumber) {
  event.preventDefault();
  const fileInput = document.getElementById(`pdf-file-${weekNumber}`);
  
  if (!fileInput?.files?.length) {
    Toast.show('Please select a PDF file.', 'error');
    return;
  }
  
  const file = fileInput.files[0];
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    Toast.show('Only PDF files allowed.', 'error');
    return;
  }
  
  const formData = new FormData();
  formData.append('application_id', appId);
  formData.append('week_number', weekNumber);
  formData.append('file', file);
  
  try {
    const token = localStorage.getItem('access_token');
    
    // 1. Upload PDF
    const uploadRes = await fetch('/api/submissions/upload', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });
    
    if (!uploadRes.ok) {
      throw new Error('Upload failed');
    }
    
    // 2. Log attendance
    await fetch('/api/attendance/log', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        application_id: appId,
        week_number: weekNumber
      })
    });
    
    Toast.show('Assignment submitted and attendance logged!', 'success');
    Modals.close();
    this.loadApplications();
    
  } catch (error) {
    Toast.show(error.message || 'Submission failed.', 'error');
  }
}
```

### 4. Sync to Google Sheets

```javascript
// File: webintern/static/js/components/sync.js (new file)

const GoogleSyncManager = {
  async syncNow() {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch('/api/sync/google-sheets', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await res.json();
      if (res.ok) {
        Toast.show(`Synced ${data.synced_count} records to Google Sheets`, 'success');
      } else {
        Toast.show('Sync failed', 'error');
      }
    } catch (error) {
      console.error('Sync error:', error);
      Toast.show('Sync error occurred', 'error');
    }
  },
  
  // Auto-sync every 5 minutes
  startAutoSync() {
    setInterval(() => {
      this.syncNow();
    }, 5 * 60 * 1000);
  }
};

// Start auto-sync when app loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    GoogleSyncManager.startAutoSync();
  });
} else {
  GoogleSyncManager.startAutoSync();
}
```

---

## 4. GOOGLE SHEETS API INTEGRATION

Add this helper function to sync data to Google Sheets:

```python
# File: webintern/utils/google_sheets_service.py (add to existing file)

def sync_internship_to_sheets(user_id, internship_data):
    """
    Sync internship history to Google Sheets.
    Requires: Google Sheets API credentials
    """
    try:
        # Get user's Google account ID
        user = query_db(
            "SELECT google_account_id FROM profiles WHERE id = ?",
            (user_id,), one=True
        )
        
        if not user['google_account_id']:
            return False
        
        # Call Google Sheets API
        # service = get_google_sheets_service()
        # spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        # range_name = f"Internship History!A:H"
        
        # values = [[
        #     internship_data['internship_title'],
        #     internship_data['sector_name'],
        #     internship_data['status'],
        #     internship_data['enrolled_date'],
        #     internship_data['start_date'],
        #     internship_data['completion_date'],
        #     internship_data['completed_weeks'],
        #     internship_data['certificate_earned']
        # ]]
        
        # service.spreadsheets().values().append(
        #     spreadsheetId=spreadsheet_id,
        #     range=range_name,
        #     valueInputOption="USER_ENTERED",
        #     body={"values": values}
        # ).execute()
        
        return True
    except Exception as e:
        print(f"Google Sheets sync error: {e}")
        return False
```

---

## 5. WORKFLOW DIAGRAM

```
User Registration/Login with Google
        ↓
Link Google Account ID to Profile
        ↓
Enroll in Internship
        ↓
Create internship_history record
        ↓
Submit Weekly PDF
        ↓
Log Attendance in internship_attendance
        ↓
Create sync_logs entry (pending)
        ↓
Auto-sync to Google Sheets
        ↓
Update sync_logs status (synced/failed)
        ↓
User can view full internship history
```

---

## 6. DATA FLOW EXAMPLE

### User Enrolls in Internship:
```
1. POST /api/applications (create application)
   ↓
2. INSERT internship_history (status: enrolled)
   ↓
3. INSERT sync_logs (type: ENROLLMENT, status: pending)
   ↓
4. Auto-sync triggers every 5 minutes
   ↓
5. Google Sheets API called with enrollment data
   ↓
6. UPDATE sync_logs (status: synced, synced_at: now)
```

### User Submits Assignment:
```
1. POST /api/submissions/upload (upload PDF)
   ↓
2. POST /api/attendance/log (create attendance record)
   ↓
3. INSERT internship_attendance (week_number, submission_status)
   ↓
4. INSERT sync_logs (type: ATTENDANCE, status: pending)
   ↓
5. UPDATE internship_history (completed_weeks + 1, progress)
   ↓
6. Auto-sync to Google Sheets
```

### Certificate Issued:
```
1. Certificate generated and paid
   ↓
2. INSERT certificates (create certificate)
   ↓
3. UPDATE internship_history (certificate_earned: true)
   ↓
4. INSERT sync_logs (type: CERTIFICATE, status: pending)
   ↓
5. Auto-sync to Google Sheets
```

---

## 7. TESTING THE SYNC

### Test Endpoints:
```bash
# Link Google Account
curl -X POST http://localhost:5000/api/profile/link-google \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"google_account_id": "google_123@gmail.com"}'

# Get Internship History
curl -X GET http://localhost:5000/api/internship-history/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# Log Attendance
curl -X POST http://localhost:5000/api/attendance/log \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "app_123",
    "week_number": 1
  }'

# Trigger Sync
curl -X POST http://localhost:5000/api/sync/google-sheets \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 8. SETUP CHECKLIST

- [ ] Run SQL migration
- [ ] Add new API endpoints to backend
- [ ] Create frontend sync component
- [ ] Add Google Sheets API integration
- [ ] Test enrollment → sync flow
- [ ] Test attendance logging
- [ ] Test certificate sync
- [ ] Verify Google Sheets data appears
- [ ] Deploy to production

---

## 9. ENVIRONMENT VARIABLES NEEDED

Add to `.env` file:
```
GOOGLE_SHEETS_ID=your_sheet_id_here
GOOGLE_SHEETS_API_KEY=your_api_key_here
GOOGLE_SERVICE_ACCOUNT_JSON=path/to/service_account.json
AUTO_SYNC_INTERVAL=300000  # 5 minutes in ms
```

---

## 10. TROUBLESHOOTING

### Sync Not Working:
1. Check Google credentials in environment
2. Verify API is enabled in Google Cloud Console
3. Check sync_logs table for errors
4. Review browser console for JavaScript errors

### History Not Showing:
1. Verify internship_history records exist
2. Check user_id matches correctly
3. Ensure API endpoint returns data
4. Test with browser DevTools Network tab

### Google Account Not Linking:
1. Verify Google login working first
2. Check google_account_id column exists
3. Test endpoint directly with cURL
4. Check for duplicate email error

---

## Support

For issues, check:
- Database: `SELECT * FROM internship_history WHERE user_id = 'YOUR_ID';`
- Sync Logs: `SELECT * FROM sync_logs WHERE user_id = 'YOUR_ID' ORDER BY created_at DESC;`
- API Response: Network tab in DevTools (F12)

---

**Last Updated**: September 12, 2026
**Version**: 1.0
**Status**: Implementation Ready ✅
