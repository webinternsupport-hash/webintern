-- Add emoji column to internships table
ALTER TABLE internships ADD COLUMN emoji TEXT DEFAULT '💼';

-- Add emojis to each internship based on their title
UPDATE internships SET emoji = '🐍' WHERE title LIKE '%Python%';
UPDATE internships SET emoji = '☕' WHERE title LIKE '%Java%';
UPDATE internships SET emoji = '⚙️' WHERE title LIKE '%C++%';
UPDATE internships SET emoji = '🐹' WHERE title LIKE '%Go%';
UPDATE internships SET emoji = '📘' WHERE title LIKE '%Node.js%' OR title LIKE '%JavaScript%';
UPDATE internships SET emoji = '🦀' WHERE title LIKE '%Rust%';
UPDATE internships SET emoji = '#️⃣' WHERE title LIKE '%C#%' OR title LIKE '.NET%';
UPDATE internships SET emoji = '🐘' WHERE title LIKE '%PHP%' OR title LIKE '%Laravel%';
UPDATE internships SET emoji = '💎' WHERE title LIKE '%Ruby%' OR title LIKE '%Rails%';
UPDATE internships SET emoji = '🎯' WHERE title LIKE '%Kotlin%';

-- Frontend Emojis
UPDATE internships SET emoji = '⚛️' WHERE title LIKE '%React%';
UPDATE internships SET emoji = '💚' WHERE title LIKE '%Vue%';
UPDATE internships SET emoji = '🅰️' WHERE title LIKE '%Angular%';
UPDATE internships SET emoji = '📘' WHERE title LIKE '%TypeScript%';
UPDATE internships SET emoji = '▲' WHERE title LIKE '%Next.js%';
UPDATE internships SET emoji = '🔥' WHERE title LIKE '%Svelte%';

-- Mobile Emojis
UPDATE internships SET emoji = '📱' WHERE title LIKE '%React Native%' OR title LIKE '%Mobile%';
UPDATE internships SET emoji = '🍎' WHERE title LIKE '%iOS%' OR title LIKE '%Swift%';
UPDATE internships SET emoji = '🤖' WHERE title LIKE '%Android%';
UPDATE internships SET emoji = '🦋' WHERE title LIKE '%Flutter%';

-- AI/ML Emojis
UPDATE internships SET emoji = '🤖' WHERE title LIKE '%AI%' OR title LIKE '%Machine Learning%' OR title LIKE '%Deep Learning%';
UPDATE internships SET emoji = '📊' WHERE title LIKE '%Data Science%' OR title LIKE '%Analytics%' OR title LIKE '%Data%';

-- DevOps & Cloud Emojis
UPDATE internships SET emoji = '☁️' WHERE title LIKE '%Cloud%' OR title LIKE '%AWS%' OR title LIKE '%Azure%';
UPDATE internships SET emoji = '🐳' WHERE title LIKE '%Docker%' OR title LIKE '%Kubernetes%' OR title LIKE '%DevOps%';

-- Cybersecurity Emojis
UPDATE internships SET emoji = '🔒' WHERE title LIKE '%Security%' OR title LIKE '%Cybersecurity%' OR title LIKE '%Hacking%';
UPDATE internships SET emoji = '🔑' WHERE title LIKE '%Blockchain%' OR title LIKE '%Web3%' OR title LIKE '%Crypto%';

-- Other Emojis
UPDATE internships SET emoji = '🎮' WHERE title LIKE '%Game%';
UPDATE internships SET emoji = '✅' WHERE title LIKE '%QA%' OR title LIKE '%Testing%';
UPDATE internships SET emoji = '💼' WHERE title LIKE '%Business%' OR title LIKE '%Management%';
UPDATE internships SET emoji = '📈' WHERE title LIKE '%Marketing%' OR title LIKE '%Digital%';
UPDATE internships SET emoji = '💰' WHERE title LIKE '%Finance%' OR title LIKE '%Banking%';
UPDATE internships SET emoji = '🎨' WHERE title LIKE '%Design%' OR title LIKE '%UI%' OR title LIKE '%UX%';

-- Verify all internships have emojis
SELECT title, emoji FROM internships WHERE emoji IS NULL;
