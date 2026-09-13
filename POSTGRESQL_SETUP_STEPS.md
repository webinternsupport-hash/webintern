# PostgreSQL Setup Instructions

Your PostgreSQL database is empty and needs the schema created first.

## Step 1: Create All Tables

**File to run FIRST: `SETUP_POSTGRESQL_DATABASE.sql`**

1. Open your PostgreSQL SQL editor/client
2. Copy entire content from `webintern/SETUP_POSTGRESQL_DATABASE.sql`
3. Paste into your SQL editor
4. Execute/Run the query

**Expected output:**
```
Tables created successfully
profiles_count: 0
sectors_count: 0
internships_count: 0
applications_count: 0
```

---

## Step 2: Add Student Persistence

**File to run SECOND: `PERSISTENCE_POSTGRESQL.sql`**

After Step 1 completes successfully:

1. Copy entire content from `webintern/PERSISTENCE_POSTGRESQL.sql`
2. Paste into your SQL editor
3. Execute/Run the query

**Expected output:**
- Data integrity report
- List of students with enrollments
- Detailed internship information
- Summary statistics

---

## Step 3: Seed Sample Data (Optional)

If you want to test with sample data:

```sql
-- Insert sample sector
INSERT INTO sectors (id, name, slug, icon_url, description) 
VALUES ('sector-1', 'Backend Development', 'backend-dev', '/icon.png', 'Server-side development');

-- Insert sample internship
INSERT INTO internships (id, sector_id, title, slug, short_description, full_description, duration_weeks)
VALUES ('int-1', 'sector-1', 'Python Backend', 'python-backend', 'Learn Python', 'Full description here', 4);

-- Insert sample student
INSERT INTO profiles (id, full_name, email, phone, college)
VALUES ('student-1', 'John Doe', 'john@example.com', '9876543210', 'MIT');

-- Insert sample enrollment
INSERT INTO applications (id, user_id, internship_id, status, applied_at, start_date, end_date)
VALUES ('app-1', 'student-1', 'int-1', 'active', CURRENT_TIMESTAMP, '2026-09-13', '2026-10-11');
```

Then verify:
```sql
SELECT * FROM applications WHERE status = 'active';
```

---

## Troubleshooting

### Error: "relation does not exist"
- Run `SETUP_POSTGRESQL_DATABASE.sql` first
- Make sure you're connected to the correct database
- Check that you're in the right schema (public)

### Error: "column does not exist"
- Make sure Step 1 completed successfully
- Run: `SELECT * FROM information_schema.tables WHERE table_schema='public';`
- This will show all created tables

### Error: "permission denied"
- You need superuser or table creation permissions
- Contact your database administrator

### No data showing
- If tables are empty, run Step 3 to seed sample data
- Or upload your actual data from CSV/JSON

---

## Quick Command Reference

### Check if tables exist
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema='public';
```

### Check table structure
```sql
\d profiles;
\d applications;
\d internships;
```

### Count records
```sql
SELECT 'Profiles' as table_name, COUNT(*) FROM profiles
UNION ALL
SELECT 'Applications', COUNT(*) FROM applications
UNION ALL
SELECT 'Internships', COUNT(*) FROM internships
UNION ALL
SELECT 'Sectors', COUNT(*) FROM sectors;
```

### Get all student enrollments
```sql
SELECT 
  p.full_name,
  p.email,
  i.title AS internship,
  a.status,
  a.applied_at
FROM applications a
JOIN profiles p ON a.user_id = p.id
JOIN internships i ON a.internship_id = i.id
WHERE a.status = 'active'
ORDER BY p.full_name;
```

---

## Files You Need

1. **SETUP_POSTGRESQL_DATABASE.sql** - Creates all tables (RUN FIRST)
2. **PERSISTENCE_POSTGRESQL.sql** - Adds persistence features (RUN SECOND)
3. **PERSISTENCE_STUDENT_INTERNSHIPS.sql** - For SQLite (don't use with PostgreSQL)

---

## Summary

```
Your Setup Workflow:
1. Run SETUP_POSTGRESQL_DATABASE.sql (creates tables)
   ↓
2. Run PERSISTENCE_POSTGRESQL.sql (adds persistence)
   ↓
3. (Optional) Seed sample data
   ↓
4. Verify with queries above
   ↓
5. ✓ Ready to use!
```

---

**Status**: Ready to setup
**Database Type**: PostgreSQL
**Next Step**: Run `SETUP_POSTGRESQL_DATABASE.sql` first
