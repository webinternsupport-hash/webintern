-- Migration: Add Internship Sync Fields for Google Account Integration
-- Purpose: Enable tracking of internship enrollment, completion, and attendance history linked to Google accounts

-- 1. Add fields to profiles table to track Google account sync
ALTER TABLE profiles ADD COLUMN google_account_id TEXT UNIQUE;
ALTER TABLE profiles ADD COLUMN last_sync_time TIMESTAMP;
ALTER TABLE profiles ADD COLUMN sync_enabled BOOLEAN DEFAULT FALSE;

-- 2. Create a new table to track internship enrollment history
CREATE TABLE IF NOT EXISTS internship_history (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  application_id VARCHAR(36),
  internship_id VARCHAR(36) NOT NULL,
  internship_title TEXT NOT NULL,
  sector_name TEXT,
  status TEXT NOT NULL DEFAULT 'enrolled', -- enrolled, attending, completed, withdrawn
  enrolled_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  start_date TIMESTAMP,
  completion_date TIMESTAMP,
  attendance_count INT DEFAULT 0,
  total_weeks INT DEFAULT 4,
  completed_weeks INT DEFAULT 0,
  progress_percentage INT DEFAULT 0,
  certificate_earned BOOLEAN DEFAULT FALSE,
  certificate_id VARCHAR(36),
  is_verified BOOLEAN DEFAULT FALSE,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES profiles(id) ON DELETE CASCADE,
  FOREIGN KEY(internship_id) REFERENCES internships(id),
  FOREIGN KEY(application_id) REFERENCES applications(id)
);

-- 3. Create table for weekly attendance tracking
CREATE TABLE IF NOT EXISTS internship_attendance (
  id VARCHAR(36) PRIMARY KEY,
  internship_history_id VARCHAR(36) NOT NULL,
  application_id VARCHAR(36),
  week_number INT NOT NULL,
  attended_date TIMESTAMP,
  submission_status TEXT DEFAULT 'pending', -- pending, submitted, approved, revise
  marks_obtained INT,
  max_marks INT DEFAULT 10,
  feedback TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(internship_history_id) REFERENCES internship_history(id) ON DELETE CASCADE,
  FOREIGN KEY(application_id) REFERENCES applications(id)
);

-- 4. Add sync tracking table for Google Sheets synchronization
CREATE TABLE IF NOT EXISTS sync_logs (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36),
  sync_type TEXT NOT NULL, -- 'ENROLLMENT', 'COMPLETION', 'ATTENDANCE', 'CERTIFICATE'
  record_id VARCHAR(36),
  status TEXT DEFAULT 'pending', -- pending, synced, failed
  error_message TEXT,
  synced_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES profiles(id)
);

-- 5. Create index for faster queries
CREATE INDEX idx_user_internship_history ON internship_history(user_id);
CREATE INDEX idx_internship_history_status ON internship_history(status);
CREATE INDEX idx_attendance_week ON internship_attendance(week_number);
CREATE INDEX idx_sync_logs_user ON sync_logs(user_id);
CREATE INDEX idx_sync_logs_status ON sync_logs(status);

-- 6. Update applications table to link internship history
ALTER TABLE applications ADD COLUMN internship_history_id VARCHAR(36);
ALTER TABLE applications ADD FOREIGN KEY (internship_history_id) REFERENCES internship_history(id);

-- Migration complete. Run this script to update your database with internship sync capability.
