-- Migration: Add Emoji Support and Enhanced Persistence Fields
-- Purpose: Enable emoji icons for internships and prevent data loss on page reload

-- 1. Ensure internships table has emoji field (already exists, but this ensures it)
-- ALTER TABLE internships ADD COLUMN IF NOT EXISTS emoji TEXT DEFAULT '💼';

-- 2. Add missing fields to applications table for better data persistence
ALTER TABLE applications ADD COLUMN IF NOT EXISTS start_date TEXT;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS end_date TEXT;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS duration_weeks INT DEFAULT 4;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS completed_weeks INT DEFAULT 0;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS progress_percent INT DEFAULT 0;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS internship_title TEXT;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS sector_name TEXT;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS internship_emoji TEXT DEFAULT '💼';
ALTER TABLE applications ADD COLUMN IF NOT EXISTS company_name TEXT;

-- 3. Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_internship ON applications(internship_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_internships_sector ON internships(sector_id);
CREATE INDEX IF NOT EXISTS idx_internships_featured ON internships(is_featured);

-- 4. Update existing applications to include internship details (denormalized for performance)
-- This should be run manually or by backend trigger when applications are created
UPDATE applications 
SET 
  internship_title = (SELECT title FROM internships WHERE internships.id = applications.internship_id),
  sector_name = (SELECT sectors.name FROM internships 
                 JOIN sectors ON internships.sector_id = sectors.id 
                 WHERE internships.id = applications.internship_id),
  internship_emoji = COALESCE((SELECT emoji FROM internships WHERE internships.id = applications.internship_id), '💼')
WHERE internship_title IS NULL;

-- 5. Set default start and end dates for existing applications (4 weeks from applied_at)
UPDATE applications 
SET 
  start_date = DATE(applied_at),
  end_date = DATE(applied_at, '+28 days'),
  duration_weeks = 4
WHERE start_date IS NULL;

-- Migration complete. Your internship data will now persist across reloads with emoji support!
