import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import sqlite3
import uuid
import json
import os
import bcrypt
from config import Config
from seed_all_database import SECTORS_DATA, slugify

def get_db_connection():
    db_path = Config.SQLITE_DB_PATH
    print(f"[DB Connection] Opening database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        
        is_serverless = os.getenv("VERCEL") == "1" or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None
        
        if not is_serverless:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            print("[DB] WAL mode enabled (local environment)")
        else:
            conn.execute("PRAGMA journal_mode=DELETE;")
            print("[DB] DELETE mode enabled (serverless environment)")
            
        # CRITICAL FIX: Verify database has tables after opening
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"[DB] Tables found: {len(tables)}")
        
        return conn
    except Exception as e:
        print(f"[DB Error] Failed to connect: {e}")
        raise

def ensure_migrations(cursor):
    """Ensure all extended tables, indexes, and columns exist for ultra-fast performance."""
    # Create performance indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_apps_user_id ON applications(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_apps_internship_id ON applications(internship_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_certs_app_id ON certificates(application_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_subs_app_id ON submissions(application_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(razorpay_order_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_app_id ON documents(application_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_student_id ON documents(student_id)")
    # Column migrations for profiles table
    try:
        cursor.execute("ALTER TABLE profiles ADD COLUMN college TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE profiles ADD COLUMN department TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE profiles ADD COLUMN degree TEXT")
    except Exception:
        pass

    # Create password_resets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id VARCHAR(36) PRIMARY KEY,
            email TEXT NOT NULL,
            token_hash TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            consumed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create documents table for document management & status tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id VARCHAR(36) PRIMARY KEY,
            application_id VARCHAR(36) NOT NULL,
            student_id VARCHAR(36) NOT NULL,
            document_type TEXT NOT NULL, -- 'OFFER_LETTER' or 'CERTIFICATE'
            document_number TEXT UNIQUE NOT NULL,
            file_path TEXT,
            status TEXT DEFAULT 'ISSUED', -- DRAFT, GENERATED, ISSUED, REVOKED
            email_status TEXT DEFAULT 'PENDING', -- PENDING, SENT, FAILED, RETRYING
            email_message_id TEXT,
            email_sent_at TIMESTAMP,
            sheets_synced BOOLEAN DEFAULT FALSE,
            sheets_synced_at TIMESTAMP,
            sheets_error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create audit_logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36),
            student_id VARCHAR(36),
            document_id VARCHAR(36),
            document_type TEXT,
            action TEXT NOT NULL,
            ip_address TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create master_internships table for Master Record System
    cursor.execute("""
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
            key_responsibilities TEXT,
            learning_outcomes TEXT,
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
        )
    """)

    # Create organization_settings table
    cursor.execute("""
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
        )
    """)

    # Seed default organization_settings row if empty
    cursor.execute("SELECT COUNT(*) FROM organization_settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO organization_settings (id, organization_name, organization_website, organization_email, founder_name, founder_designation, technical_director_name, technical_director_designation)
            VALUES ('default', 'WebIntern', 'www.webintern.in', 'webinternsupport@gmail.com', 'Founding Board', 'Founder', 'Dr. A. K. Sharma', 'Technical Director')
        """)

    # Create contact_messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id VARCHAR(36) PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            subject TEXT,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'UNREAD',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    def _add_col(table, col_name, col_def):
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cursor.fetchall()]
        if col_name not in cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")

    # Profiles extensions
    _add_col('profiles', 'password_hash', 'TEXT')
    _add_col('profiles', 'auth_provider', "TEXT DEFAULT 'email'")
    _add_col('profiles', 'mobile', 'TEXT')
    _add_col('profiles', 'terms_accepted', 'BOOLEAN DEFAULT FALSE')
    _add_col('profiles', 'google_account_id', 'TEXT')
    _add_col('profiles', 'sync_enabled', 'BOOLEAN DEFAULT TRUE')
    _add_col('profiles', 'last_sync_time', 'TIMESTAMP')

    # Internships extensions
    _add_col('internships', 'company_name', "TEXT DEFAULT 'Web Intern Platform'")
    _add_col('internships', 'location', "TEXT DEFAULT 'Virtual / Remote'")
    _add_col('internships', 'guide_name', "TEXT DEFAULT 'Dr. A. K. Sharma (Technical Director)'")
    _add_col('internships', 'skills_tools', "TEXT DEFAULT 'Python, Web Development, Analytics, Cloud'")
    _add_col('internships', 'tasks_projects', "TEXT DEFAULT 'Industry Capstone Project & Weekly Deliverables'")
    _add_col('internships', 'project_name', "TEXT DEFAULT 'Enterprise Internship Project'")
    _add_col('internships', 'certificate_eligible', 'BOOLEAN DEFAULT TRUE')
    _add_col('internships', 'active', 'BOOLEAN DEFAULT TRUE')
    _add_col('internships', 'internship_emoji', "TEXT DEFAULT '💼'")

    # Applications / Enrollments extensions
    _add_col('applications', 'start_date', 'TEXT')
    _add_col('applications', 'end_date', 'TEXT')
    _add_col('applications', 'offer_letter_id', 'TEXT')
    _add_col('applications', 'certificate_id', 'TEXT')
    _add_col('applications', 'completion_status', "TEXT DEFAULT 'pending'")
    _add_col('applications', 'google_sync_status', "TEXT DEFAULT 'not_synced'")
    _add_col('applications', 'last_synced_at', 'TIMESTAMP')

    # Submissions extensions
    _add_col('submissions', 'marks', 'REAL')
    _add_col('submissions', 'max_marks', 'REAL DEFAULT 10')
    _add_col('submissions', 'graded_by', 'TEXT')
    _add_col('submissions', 'graded_at', 'TEXT')
    _add_col('submissions', 'original_file_name', 'TEXT')
    _add_col('submissions', 'file_size', 'INTEGER')

    # ========================================================
    # Documents.file_path NOT NULL → nullable migration
    # (SQLite doesn't support ALTER COLUMN, so rebuild table.)
    # ========================================================
    try:
        cursor.execute("PRAGMA table_info(documents)")
        cols = cursor.fetchall()
        file_path_col = next((c for c in cols if c[1] == 'file_path'), None)
        if file_path_col and file_path_col[3] == 1:  # notnull flag == 1
            print("[DB Migration] Rebuilding documents table to make file_path nullable...")
            cursor.executescript("""
                PRAGMA foreign_keys = OFF;
                CREATE TABLE IF NOT EXISTS documents_new (
                    id VARCHAR(36) PRIMARY KEY,
                    application_id VARCHAR(36) NOT NULL,
                    student_id VARCHAR(36) NOT NULL,
                    document_type TEXT NOT NULL,
                    document_number TEXT UNIQUE NOT NULL,
                    file_path TEXT,
                    status TEXT DEFAULT 'ISSUED',
                    email_status TEXT DEFAULT 'PENDING',
                    email_message_id TEXT,
                    email_sent_at TIMESTAMP,
                    sheets_synced BOOLEAN DEFAULT FALSE,
                    sheets_synced_at TIMESTAMP,
                    sheets_error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                INSERT OR IGNORE INTO documents_new
                  (id, application_id, student_id, document_type, document_number, file_path, status,
                   email_status, email_message_id, email_sent_at, sheets_synced, sheets_synced_at,
                   sheets_error, created_at, updated_at)
                SELECT id, application_id, student_id, document_type, document_number,
                       COALESCE(file_path, ''), status, email_status, email_message_id,
                       email_sent_at, sheets_synced, sheets_synced_at, sheets_error,
                       created_at, updated_at
                FROM documents;
                DROP TABLE documents;
                ALTER TABLE documents_new RENAME TO documents;
                PRAGMA foreign_keys = ON;
            """)
            print("[DB Migration] documents.file_path now nullable OK")
    except Exception as doc_mig_err:
        print(f"[DB Migration Warning] documents rebuild skipped: {doc_mig_err}")

EMBEDDED_SCHEMA_SQL = """
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
  purpose TEXT NOT NULL,
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
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS internship_tasks (
  id VARCHAR(36) PRIMARY KEY,
  internship_id VARCHAR(36) REFERENCES internships(id) ON DELETE CASCADE,
  week_number INT NOT NULL,
  title TEXT NOT NULL,
  objective TEXT,
  deliverables TEXT,
  key_steps TEXT,
  evaluation_criteria TEXT
);

CREATE TABLE IF NOT EXISTS applications (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) REFERENCES profiles(id) ON DELETE CASCADE,
  internship_id VARCHAR(36) REFERENCES internships(id),
  status TEXT DEFAULT 'active',
  offer_letter_sent BOOLEAN DEFAULT FALSE,
  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
  status TEXT DEFAULT 'created',
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
"""

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if sectors table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sectors'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
            schema_sql = None
            if os.path.exists(schema_path):
                try:
                    with open(schema_path, "r", encoding="utf-8") as f:
                        schema_sql = f.read()
                except Exception as e:
                    print(f"Warning: Could not read schema.sql: {e}")
            if not schema_sql:
                schema_sql = EMBEDDED_SCHEMA_SQL
            cursor.executescript(schema_sql)
            conn.commit()

        # Always ensure migrations
        ensure_migrations(cursor)
        conn.commit()

        # Always check if data is seeded (sectors table is empty), and seed if needed
        cursor.execute("SELECT COUNT(*) FROM sectors")
        sector_count = cursor.fetchone()[0]
        
        if sector_count == 0:
            seed_data(cursor)
            conn.commit()

        conn.close()
    except Exception as e:
        print(f"Warning: Database init skipped or failed gracefully: {e}")

def seed_data(cursor):
    # Admin Seed
    admin_id = str(uuid.uuid4())
    hashed_pwd = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute(
        "INSERT INTO admins (id, email, password_hash, full_name) VALUES (?, ?, ?, ?)",
        (admin_id, "admin@webintern.com", hashed_pwd, "Platform Administrator")
    )

    used_slugs = set()

    for sec_data in SECTORS_DATA:
        sec_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO sectors (id, name, slug, icon_url, description) VALUES (?, ?, ?, ?, ?)",
            (sec_id, sec_data["name"], sec_data["slug"], sec_data["icon"], sec_data["description"])
        )

        for idx, title in enumerate(sec_data["internships"]):
            int_id = str(uuid.uuid4())
            base_slug = slugify(title)
            
            if base_slug in used_slugs:
                int_slug = f"{sec_data['slug']}-{base_slug}"
            else:
                int_slug = base_slug

            used_slugs.add(int_slug)

            short_desc = f"Gain hands-on practical project exposure in {title} through a 4-week structured virtual program."
            full_desc = f"This 4-week Virtual Internship program in {title} provides immersive industry training in {sec_data['name']}. You will complete weekly tasks, receive constructive evaluator feedback, and build a portfolio."
            is_featured = 1 if idx < 2 else 0

            cursor.execute(
                "INSERT INTO internships (id, sector_id, title, slug, short_description, full_description, duration_weeks, mode, cover_image_url, is_featured) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (int_id, sec_id, title, int_slug, short_desc, full_desc, 4, 'Virtual', f"{int_slug}-cover.jpg", is_featured)
            )

            # Weekly tasks for this internship (Domain-Specific Blueprint)
            from utils.task_templates import get_domain_tasks
            tasks = get_domain_tasks(title, sec_data["name"])

            for week, task_title, obj, deliv, steps, criteria in tasks:
                cursor.execute(
                    "INSERT INTO internship_tasks (id, internship_id, week_number, title, objective, deliverables, key_steps, evaluation_criteria) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (str(uuid.uuid4()), int_id, week, task_title, obj, deliv, steps, criteria)
                )

    # Site Stats Seed (Section 4A 2x2 Grid)
    stats = [
        ("Happy Users", "1 Lakh+", "users", 1),
        ("Job-Role Match Rate", "97%", "target", 2),
        ("Skill Improvement", "98%", "trending-up", 3),
        ("Verified Program", "Web Intern", "shield-check", 4)
    ]
    for label, val, icon, order in stats:
        cursor.execute(
            "INSERT INTO site_stats (id, label, value, icon_name, sort_order) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), label, val, icon, order)
        )

    # Product Seed
    cursor.execute(
        "INSERT INTO products (id, name, description, price_inr, is_active) VALUES (?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), "Verified & Printed Certificate Upgrade", "Get an official tamper-proof QR-verified digital certificate with optional high-quality physical hardcopy delivery to your doorstep.", 499, True)
    )

    # Testimonials Seed
    testimonials = [
        ("Ananya Sharma", "Full Stack Intern", "Web Intern gave me hands-on practical project experience! Receiving my offer letter immediately and working through weekly tasks prepared me directly for software developer interviews.", 5, "avatar1.jpg"),
        ("Rahul Verma", "Data Analytics Intern", "The weekly task evaluations and detailed admin feedback were invaluable. I earned a verified certificate that I proudly showcased on my LinkedIn profile!", 5, "avatar2.jpg"),
        ("Priya Nair", "UI/UX Design Intern", "Building real portfolio projects with real feedback completely transformed my confidence as a product designer. Highly recommended for students!", 5, "avatar3.jpg")
    ]
    for name, role, quote, rating, photo in testimonials:
        cursor.execute(
            "INSERT INTO testimonials (id, name, role, quote, rating, photo_url, is_published) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), name, role, quote, rating, photo, True)
        )

def query_db(query, args=(), one=False):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, args)
        rv = cursor.fetchall()
        conn.close()
        return (dict(rv[0]) if rv else None) if one else [dict(r) for r in rv]
    except sqlite3.OperationalError as oe:
        err_str = str(oe).lower()
        if 'no such table' in err_str or 'no such column' in err_str:
            print(f"[DB Self-Healing]: Operational error during query ({oe}). Re-initializing DB...")
            init_db()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query, args)
            rv = cursor.fetchall()
            conn.close()
            return (dict(rv[0]) if rv else None) if one else [dict(r) for r in rv]
        raise

def execute_db(query, args=()):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id
    except sqlite3.OperationalError as oe:
        err_str = str(oe).lower()
        if 'no such table' in err_str or 'no such column' in err_str:
            print(f"[DB Self-Healing]: Operational error during execute ({oe}). Re-initializing DB...")
            init_db()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
        raise
