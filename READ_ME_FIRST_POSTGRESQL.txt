================================================================================
                    POSTGRESQL DATABASE SETUP
                   FOR STUDENT INTERNSHIP PERSISTENCE
================================================================================

YOU ARE HERE BECAUSE:
- Your database is PostgreSQL (not SQLite)
- Student internships were disappearing after logout/reload
- You need to fix data persistence

SOLUTION IN 2 STEPS:

================================================================================
                              STEP 1 OF 2
================================================================================

FILE: POSTGRESQL_COPY_PASTE_STEP1.txt

1. Open that file
2. Copy ALL the SQL code
3. Paste into your PostgreSQL SQL Editor
4. Click "Run" or "Execute"

EXPECTED RESULT:
✓ No errors
✓ "Tables created successfully" message
✓ All counts show 0

If you see errors:
- Make sure you're in PostgreSQL (not MySQL or SQLite)
- Check you have database admin permissions
- Contact your database administrator

================================================================================
                              STEP 2 OF 2
================================================================================

FILE: POSTGRESQL_COPY_PASTE_STEP2.txt

1. Open that file (only after Step 1 works!)
2. Copy ALL the SQL code
3. Paste into your PostgreSQL SQL Editor
4. Click "Run" or "Execute"

EXPECTED RESULT:
✓ No errors
✓ 4 tables with data reports
✓ Shows all student enrollments

COMPLETION:
✓ Database setup complete
✓ Student data now persists
✓ No more data loss on logout/reload

================================================================================
                            TROUBLESHOOTING
================================================================================

PROBLEM: "relation does not exist"
SOLUTION: Run Step 1 first to create all tables

PROBLEM: "permission denied"
SOLUTION: You need database admin permissions
         Contact your database administrator

PROBLEM: "syntax error"
SOLUTION: Make sure you copied the ENTIRE code block
         Don't skip any lines

PROBLEM: Step 1 works but Step 2 fails
SOLUTION: Run Step 2 in the same PostgreSQL session
         Don't disconnect between steps

================================================================================
                              QUICK LINKS
================================================================================

Setup Instructions:
  → POSTGRESQL_SETUP_STEPS.md

Step 1 (Create Tables):
  → POSTGRESQL_COPY_PASTE_STEP1.txt

Step 2 (Add Persistence):
  → POSTGRESQL_COPY_PASTE_STEP2.txt

Full SQL Files:
  → SETUP_POSTGRESQL_DATABASE.sql
  → PERSISTENCE_POSTGRESQL.sql

For SQLite Users:
  → PERSISTENCE_STUDENT_INTERNSHIPS.sql

================================================================================
                          WHAT HAPPENS NEXT
================================================================================

BEFORE FIX (Problem):
Student enrolls → Data saved to browser only
                ↓
Student logout/reload → Data LOST ✗
                ↓
Student login again → No internships visible

AFTER FIX (Solution):
Student enrolls → Data saved to PostgreSQL database
              ↓
Student logout/reload → Data in database ✓
              ↓
Student login again → All internships visible ✓

================================================================================
                          TIMELINE
================================================================================

Time needed: 5-10 minutes
Difficulty: Easy (copy-paste)
Risk level: None (no data loss)

Step 1: 2-3 minutes
Step 2: 2-3 minutes
Verify: 1-2 minutes

Total: ~5 minutes

================================================================================
                          NEED HELP?
================================================================================

If you get stuck:

1. Check the error message carefully
2. Read the troubleshooting section above
3. Verify you're running PostgreSQL (not SQLite/MySQL)
4. Make sure you ran Step 1 before Step 2
5. Check you have database permissions

Contact your database administrator if:
- You don't have permissions
- PostgreSQL is down/unavailable
- You need schema in specific location

================================================================================
                          READY TO START?
================================================================================

Open: POSTGRESQL_COPY_PASTE_STEP1.txt

Copy → Paste → Run

Then come back here for Step 2!

================================================================================
