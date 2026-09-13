-- STUDENT INTERNSHIP PERSISTENCE - PostgreSQL Version
-- This file is specifically for PostgreSQL databases

-- Step 1: Ensure profiles table has all required columns
-- If email column is missing, add it
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email TEXT UNIQUE;

-- Step 2: Create indexes for fast retrieval
CREATE INDEX IF NOT EXISTS idx_applications_user_status_created 
  ON applications(user_id, status);
  
CREATE INDEX IF NOT EXISTS idx_profiles_email 
  ON profiles(email);
  
CREATE INDEX IF NOT EXISTS idx_internships_id 
  ON internships(id);

-- Step 3: Ensure applications table has sync columns
ALTER TABLE applications ADD COLUMN IF NOT EXISTS last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS is_synced_to_indexeddb BOOLEAN DEFAULT TRUE;

-- Step 4: Update sync status
UPDATE applications 
SET last_synced_at = CURRENT_TIMESTAMP, is_synced_to_indexeddb = TRUE
WHERE user_id IS NOT NULL AND user_id != '';

-- Step 5: Get data integrity report
SELECT 
  COUNT(*) AS total_applications,
  COUNT(DISTINCT user_id) AS unique_students,
  COUNT(DISTINCT internship_id) AS unique_internships,
  COUNT(CASE WHEN user_id IS NULL OR user_id = '' THEN 1 END) AS orphaned_records,
  COUNT(CASE WHEN status = 'active' THEN 1 END) AS active_enrollments
FROM applications;

-- Step 6: List all students with active enrollments
SELECT 
  p.full_name,
  p.email,
  p.college,
  COUNT(a.id) AS enrolled_internships
FROM profiles p
LEFT JOIN applications a ON p.id = a.user_id AND a.status = 'active'
GROUP BY p.id, p.full_name, p.email, p.college
HAVING COUNT(a.id) > 0
ORDER BY p.full_name;

-- Step 7: Get detailed internship information for all active students
SELECT 
  p.full_name AS student_name,
  p.email AS student_email,
  p.phone AS student_phone,
  p.college AS student_college,
  a.id AS application_id,
  a.internship_id,
  a.status AS enrollment_status,
  a.applied_at AS enrollment_date,
  a.start_date,
  a.end_date,
  a.offer_letter_sent,
  a.certificate_id,
  i.title AS internship_full_title,
  s.name AS sector_name_full
FROM profiles p
LEFT JOIN applications a ON p.id = a.user_id AND a.status = 'active'
LEFT JOIN internships i ON a.internship_id = i.id
LEFT JOIN sectors s ON i.sector_id = s.id
WHERE a.id IS NOT NULL
ORDER BY p.full_name, a.applied_at DESC;

-- Step 8: Get summary statistics
SELECT 
  COUNT(DISTINCT p.id) AS total_students,
  COUNT(DISTINCT a.id) AS total_enrollments,
  COUNT(DISTINCT CASE WHEN a.status = 'active' THEN a.id END) AS active_enrollments,
  COUNT(DISTINCT CASE WHEN a.status = 'completed' THEN a.id END) AS completed_enrollments
FROM profiles p
LEFT JOIN applications a ON p.id = a.user_id;
