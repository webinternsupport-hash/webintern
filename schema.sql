-- Web Intern Platform Database Schema (PostgreSQL & SQLite compatible)

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

CREATE TABLE IF NOT EXISTS admins (
  id VARCHAR(36) PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  full_name TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS otp_codes (
  id VARCHAR(36) PRIMARY KEY,
  email TEXT NOT NULL,
  code_hash TEXT NOT NULL,
  purpose TEXT NOT NULL, -- 'register' | 'login'
  expires_at TIMESTAMP NOT NULL,
  consumed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sectors (
  id VARCHAR(36) PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  icon_url TEXT,
  description TEXT
);

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

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_internships_sector ON internships(sector_id);
CREATE INDEX IF NOT EXISTS idx_internships_featured ON internships(is_featured);

CREATE TABLE IF NOT EXISTS internship_tasks (
  id VARCHAR(36) PRIMARY KEY,
  internship_id VARCHAR(36) REFERENCES internships(id) ON DELETE CASCADE,
  week_number INT NOT NULL,
  title TEXT NOT NULL,
  objective TEXT,
  deliverables TEXT,
  key_steps TEXT, -- JSON string or comma-separated steps
  evaluation_criteria TEXT
);

CREATE TABLE IF NOT EXISTS applications (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) REFERENCES profiles(id) ON DELETE CASCADE,
  internship_id VARCHAR(36) REFERENCES internships(id),
  status TEXT DEFAULT 'active', -- active, completed, withdrawn
  offer_letter_sent BOOLEAN DEFAULT FALSE,
  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  start_date TEXT,
  end_date TEXT,
  duration_weeks INT DEFAULT 4,
  completed_weeks INT DEFAULT 0,
  progress_percent INT DEFAULT 0,
  internship_title TEXT,
  sector_name TEXT,
  internship_emoji TEXT DEFAULT '💼',
  offer_letter_id TEXT,
  certificate_id TEXT,
  completion_status TEXT DEFAULT 'pending'
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_internship ON applications(internship_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_offer_letter ON applications(offer_letter_id);
CREATE INDEX IF NOT EXISTS idx_applications_certificate ON applications(certificate_id);

CREATE TABLE IF NOT EXISTS submissions (
  id VARCHAR(36) PRIMARY KEY,
  application_id VARCHAR(36) REFERENCES applications(id) ON DELETE CASCADE,
  week_number INT NOT NULL,
  file_url TEXT,
  status TEXT DEFAULT 'pending', -- pending, approved, revise
  feedback TEXT,
  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  reviewed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS certificates (
  id VARCHAR(36) PRIMARY KEY,
  application_id VARCHAR(36) REFERENCES applications(id),
  certificate_url TEXT,
  is_verified_paid BOOLEAN DEFAULT FALSE,
  issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
  id VARCHAR(36) PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  price_inr INT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS payments (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) REFERENCES profiles(id),
  certificate_id VARCHAR(36) REFERENCES certificates(id),
  product_id VARCHAR(36) REFERENCES products(id),
  razorpay_order_id TEXT NOT NULL,
  razorpay_payment_id TEXT,
  razorpay_signature TEXT,
  amount_inr INT NOT NULL,
  status TEXT DEFAULT 'created', -- created, paid, failed, refunded
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS newsletter_subscribers (
  id VARCHAR(36) PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS testimonials (
  id VARCHAR(36) PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT,
  quote TEXT NOT NULL,
  rating INT DEFAULT 5,
  photo_url TEXT,
  source_link TEXT,
  is_published BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS site_stats (
  id VARCHAR(36) PRIMARY KEY,
  label TEXT NOT NULL,
  value TEXT NOT NULL,
  icon_name TEXT,
  sort_order INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS master_internships (
  id VARCHAR(36) PRIMARY KEY,
  student_full_name TEXT NOT NULL,
  student_email TEXT NOT NULL,
  student_mobile TEXT,
  student_gender TEXT,
  student_date_of_birth TEXT,
  student_id TEXT,
  roll_number TEXT,
  college_name TEXT NOT NULL,
  university_name TEXT,
  degree TEXT NOT NULL,
  department TEXT NOT NULL,
  year_of_study TEXT,
  semester TEXT,
  academic_year TEXT,
  college_location TEXT,
  internship_domain TEXT,
  internship_position TEXT NOT NULL,
  internship_mode TEXT DEFAULT 'Online',
  internship_start_date TEXT NOT NULL,
  internship_end_date TEXT NOT NULL,
  internship_duration TEXT NOT NULL,
  internship_status TEXT DEFAULT 'Completed',
  project_title TEXT NOT NULL,
  project_description TEXT,
  technologies_used TEXT,
  project_category TEXT,
  key_responsibilities TEXT, -- JSON array string
  learning_outcomes TEXT,    -- JSON array string
  mentor_name TEXT NOT NULL,
  mentor_designation TEXT,
  mentor_department TEXT,
  offer_id TEXT UNIQUE NOT NULL,
  certificate_id TEXT UNIQUE NOT NULL,
  offer_letter_issue_date TEXT,
  certificate_issue_date TEXT,
  user_id VARCHAR(36),
  application_id VARCHAR(36),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS organization_settings (
  id VARCHAR(36) PRIMARY KEY DEFAULT 'default',
  organization_name TEXT NOT NULL DEFAULT 'WebIntern',
  organization_website TEXT DEFAULT 'www.webintern.in',
  organization_email TEXT DEFAULT 'webinternsupport@gmail.com',
  organization_address TEXT DEFAULT 'Virtual Learning Platform',
  founder_name TEXT DEFAULT 'Founding Board',
  founder_designation TEXT DEFAULT 'Founder',
  technical_director_name TEXT DEFAULT 'Dr. A. K. Sharma',
  technical_director_designation TEXT DEFAULT 'Technical Director',
  msme_information TEXT DEFAULT 'Ministry of MSME, Govt. of India',
  logo TEXT DEFAULT '/assets/logo.png',
  msme_logo TEXT DEFAULT '/assets/msme-logo.png',
  founder_signature TEXT DEFAULT '/assets/signature.png',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS issued_snapshots (
  id VARCHAR(36) PRIMARY KEY,
  master_record_id VARCHAR(36) NOT NULL,
  document_type TEXT NOT NULL, -- 'OFFER_LETTER' or 'CERTIFICATE'
  document_number TEXT UNIQUE NOT NULL,
  issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data_snapshot TEXT NOT NULL, -- Full JSON snapshot of record + org settings
  file_path TEXT NOT NULL
);

