-- Quick Setup: Add Emojis to All Internships
-- Run this after MIGRATION_ADD_EMOJI_AND_PERSISTENCE.sql

-- Update internships with sector-specific emojis
-- You can customize these based on your actual sector names

-- Engineering & Technology Sector
UPDATE internships 
SET emoji = '💻' 
WHERE sector_id IN (
  SELECT id FROM sectors WHERE name LIKE '%Engineering%' OR name LIKE '%Technology%'
);

-- Computer Science & IT
UPDATE internships 
SET emoji = '🖥️' 
WHERE title LIKE '%Computer%' OR title LIKE '%Software%' OR title LIKE '%IT%';

-- AI & Machine Learning
UPDATE internships 
SET emoji = '🤖' 
WHERE title LIKE '%AI%' OR title LIKE '%Machine Learning%' OR title LIKE '%ML%' OR title LIKE '%Artificial Intelligence%';

-- Data Science & Analytics
UPDATE internships 
SET emoji = '📊' 
WHERE title LIKE '%Data Science%' OR title LIKE '%Analytics%' OR title LIKE '%Data Analyst%';

-- Web Development
UPDATE internships 
SET emoji = '🌐' 
WHERE title LIKE '%Web Development%' OR title LIKE '%Frontend%' OR title LIKE '%Backend%' OR title LIKE '%Full Stack%';

-- Mobile App Development
UPDATE internships 
SET emoji = '📱' 
WHERE title LIKE '%Mobile%' OR title LIKE '%Android%' OR title LIKE '%iOS%' OR title LIKE '%App Development%';

-- Management & Commerce Sector
UPDATE internships 
SET emoji = '💼' 
WHERE sector_id IN (
  SELECT id FROM sectors WHERE name LIKE '%Management%' OR name LIKE '%Commerce%' OR name LIKE '%Business%'
);

-- Marketing & Sales
UPDATE internships 
SET emoji = '📣' 
WHERE title LIKE '%Marketing%' OR title LIKE '%Sales%' OR title LIKE '%Advertising%';

-- Finance & Accounting
UPDATE internships 
SET emoji = '💰' 
WHERE title LIKE '%Finance%' OR title LIKE '%Accounting%' OR title LIKE '%Banking%';

-- Human Resources
UPDATE internships 
SET emoji = '👥' 
WHERE title LIKE '%HR%' OR title LIKE '%Human Resource%' OR title LIKE '%Recruitment%';

-- Science Sector
UPDATE internships 
SET emoji = '🔬' 
WHERE sector_id IN (
  SELECT id FROM sectors WHERE name LIKE '%Science%'
);

-- Biology & Life Sciences
UPDATE internships 
SET emoji = '🧬' 
WHERE title LIKE '%Biology%' OR title LIKE '%Biotechnology%' OR title LIKE '%Genetics%';

-- Chemistry
UPDATE internships 
SET emoji = '⚗️' 
WHERE title LIKE '%Chemistry%' OR title LIKE '%Chemical%';

-- Physics
UPDATE internships 
SET emoji = '⚛️' 
WHERE title LIKE '%Physics%' OR title LIKE '%Quantum%';

-- Medical & Healthcare Sector
UPDATE internships 
SET emoji = '⚕️' 
WHERE sector_id IN (
  SELECT id FROM sectors WHERE name LIKE '%Medical%' OR name LIKE '%Healthcare%' OR name LIKE '%Health%'
);

-- Nursing
UPDATE internships 
SET emoji = '👩‍⚕️' 
WHERE title LIKE '%Nursing%' OR title LIKE '%Nurse%';

-- Pharmacy
UPDATE internships 
SET emoji = '💊' 
WHERE title LIKE '%Pharmacy%' OR title LIKE '%Pharmaceutical%';

-- Arts & Design
UPDATE internships 
SET emoji = '🎨' 
WHERE title LIKE '%Design%' OR title LIKE '%Graphic%' OR title LIKE '%UI%' OR title LIKE '%UX%' OR title LIKE '%Creative%';

-- Content Writing
UPDATE internships 
SET emoji = '✍️' 
WHERE title LIKE '%Content%' OR title LIKE '%Writing%' OR title LIKE '%Copywriting%';

-- Video Editing
UPDATE internships 
SET emoji = '🎬' 
WHERE title LIKE '%Video%' OR title LIKE '%Editing%' OR title LIKE '%Filmmaker%';

-- Civil Engineering
UPDATE internships 
SET emoji = '🏗️' 
WHERE title LIKE '%Civil%' OR title LIKE '%Construction%' OR title LIKE '%Architecture%';

-- Mechanical Engineering
UPDATE internships 
SET emoji = '⚙️' 
WHERE title LIKE '%Mechanical%' OR title LIKE '%Manufacturing%';

-- Electrical Engineering
UPDATE internships 
SET emoji = '⚡' 
WHERE title LIKE '%Electrical%' OR title LIKE '%Electronics%' OR title LIKE '%Power%';

-- Cybersecurity
UPDATE internships 
SET emoji = '🔒' 
WHERE title LIKE '%Cyber%' OR title LIKE '%Security%' OR title LIKE '%Ethical Hacking%';

-- Blockchain & Cryptocurrency
UPDATE internships 
SET emoji = '₿' 
WHERE title LIKE '%Blockchain%' OR title LIKE '%Crypto%' OR title LIKE '%Web3%';

-- Environmental Science
UPDATE internships 
SET emoji = '🌱' 
WHERE title LIKE '%Environmental%' OR title LIKE '%Sustainability%' OR title LIKE '%Green%';

-- Law & Legal
UPDATE internships 
SET emoji = '⚖️' 
WHERE title LIKE '%Law%' OR title LIKE '%Legal%' OR title LIKE '%Advocate%';

-- Education & Teaching
UPDATE internships 
SET emoji = '📚' 
WHERE title LIKE '%Education%' OR title LIKE '%Teaching%' OR title LIKE '%Tutor%';

-- Research
UPDATE internships 
SET emoji = '🔍' 
WHERE title LIKE '%Research%';

-- Project Management
UPDATE internships 
SET emoji = '📋' 
WHERE title LIKE '%Project Management%' OR title LIKE '%PM%' OR title LIKE '%Scrum%';

-- Cloud Computing
UPDATE internships 
SET emoji = '☁️' 
WHERE title LIKE '%Cloud%' OR title LIKE '%AWS%' OR title LIKE '%Azure%' OR title LIKE '%GCP%';

-- IoT (Internet of Things)
UPDATE internships 
SET emoji = '🌐' 
WHERE title LIKE '%IoT%' OR title LIKE '%Internet of Things%';

-- Robotics
UPDATE internships 
SET emoji = '🤖' 
WHERE title LIKE '%Robot%' OR title LIKE '%Automation%';

-- Gaming
UPDATE internships 
SET emoji = '🎮' 
WHERE title LIKE '%Game%' OR title LIKE '%Gaming%' OR title LIKE '%Unity%';

-- Photography
UPDATE internships 
SET emoji = '📷' 
WHERE title LIKE '%Photography%' OR title LIKE '%Photographer%';

-- Social Media Management
UPDATE internships 
SET emoji = '📲' 
WHERE title LIKE '%Social Media%' OR title LIKE '%SMM%';

-- Default for any remaining internships
UPDATE internships 
SET emoji = '💼' 
WHERE emoji IS NULL OR emoji = '';

-- Verify the update
SELECT 
  i.title,
  i.emoji,
  s.name as sector_name
FROM internships i
LEFT JOIN sectors s ON i.sector_id = s.id
ORDER BY s.name, i.title;

-- Success message
SELECT 'All internships have been updated with emojis! 🎉' as message;
