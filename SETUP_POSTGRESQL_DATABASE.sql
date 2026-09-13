-- COMPLETE PostgreSQL Database Setup for WebIntern
-- Run this FIRST to create all tables, then run PERSISTENCE_POSTGRESQL.sql

-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id VARCHAR(36) PRIMARY KEY,
  full_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  phone TEXT,
  phone_country_code TEXT DEFAULT '+91',
  college TEXT,
  avatar_url TEXT,
  marketing_opt_in BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sectors table
CREATE TABLE IF NOT EXISTS sectors (
  id VARCHAR(36) PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  icon_url TEXT,
  description TEXT
);

-- Create internships table
CREATE TABLE IF NOT EXISTS internships (
  id VARCHAR(36) PRIMARY KEY,
  sector_id VARCHAR(36) REFERENCES sectors(id),
  title TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  short_description TEXT,
  full_description TEXT,
  duration_weeks INT DEFAULT 4,
  mode TEXT DEFAULT 'Virtual',
  cover_image_url TEXT,
  is_featured BOOLEAN DEFAULT FALSE,
  emoji TEXT DEFAULT '💼',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create applications table
CREATE TABLE IF NOT EXISTS applications (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) REFERENCES profiles(id) ON DELETE CASCADE,
  internship_id VARCHAR(36) REFERENCES internships(id),
  status TEXT DEFAULT 'active',
  offer_letter_sent BOOLEAN DEFAULT FALSE,
  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  start_date TEXT,
  end_date TEXT,
  offer_letter_id TEXT,
  certificate_id TEXT,
  completion_status TEXT DEFAULT 'pending',
  google_sync_status TEXT DEFAULT 'not_synced',
  last_synced_at TIMESTAMP,
  is_synced_to_indexeddb BOOLEAN DEFAULT TRUE
);

-- Create submissions table
CREATE TABLE IF NOT EXISTS submissions (
  id VARCHAR(36) PRIMARY KEY,
  application_id VARCHAR(36) REFERENCES applications(id) ON DELETE CASCADE,
  week_number INT NOT NULL,
  file_url TEXT,
  status TEXT DEFAULT 'pending',
  feedback TEXT,
  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  reviewed_at TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_applications_user_status_created 
  ON applications(user_id, status);
  
CREATE INDEX IF NOT EXISTS idx_profiles_email 
  ON profiles(email);
  
CREATE INDEX IF NOT EXISTS idx_internships_id 
  ON internships(id);
  
CREATE INDEX IF NOT EXISTS idx_applications_internship 
  ON applications(internship_id);
  
CREATE INDEX IF NOT EXISTS idx_submissions_application 
  ON submissions(application_id);

-- Confirm tables created
SELECT 
  'Tables created successfully' AS status,
  (SELECT COUNT(*) FROM profiles) AS profiles_count,
  (SELECT COUNT(*) FROM sectors) AS sectors_count,
  (SELECT COUNT(*) FROM internships) AS internships_count,
  (SELECT COUNT(*) FROM applications) AS applications_count;
