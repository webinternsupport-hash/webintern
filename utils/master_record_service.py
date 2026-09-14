import uuid
import json
import datetime
import re
from database import query_db, execute_db

def parse_date_safely(date_str):
    if not date_str:
        return None
    date_str = str(date_str).strip()
    for fmt in ["%B %d, %Y", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d %B %Y"]:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except Exception:
            pass
    return None

def calculate_duration(start_date_str, end_date_str):
    start_dt = parse_date_safely(start_date_str)
    end_dt = parse_date_safely(end_date_str)
    if not start_dt or not end_dt:
        return "4 Weeks"
    
    diff_days = (end_dt - start_dt).days
    if diff_days <= 0:
        return "4 Weeks"
    
    weeks = max(1, round(diff_days / 7.0))
    return f"{weeks} Weeks"

def format_date_human(date_str):
    dt = parse_date_safely(date_str)
    if not dt:
        return date_str or ""
    return dt.strftime("%B %d, %Y")

def generate_unique_offer_id():
    suffix = uuid.uuid4().hex[:6].upper()
    return f"WI-OFFER-2026-{suffix}"

def generate_unique_certificate_id():
    suffix = uuid.uuid4().hex[:6].upper()
    return f"WI-CERT-2026-{suffix}"

def get_organization_settings():
    settings = query_db("SELECT * FROM organization_settings WHERE id = 'default'", one=True)
    if not settings:
        return {
            "id": "default",
            "organization_name": "WebIntern",
            "organization_website": "www.webintern.in",
            "organization_email": "webinternsupport@gmail.com",
            "organization_address": "Virtual Learning Platform",
            "founder_name": "Founding Board",
            "founder_designation": "Founder",
            "technical_director_name": "Dr. A. K. Sharma",
            "technical_director_designation": "Technical Director",
            "msme_information": "Ministry of MSME, Govt. of India",
            "logo": "/assets/logo.png",
            "msme_logo": "/assets/msme-logo.png",
            "founder_signature": "/assets/signature.png"
        }
    return settings

def update_organization_settings(data):
    org = get_organization_settings()
    name = (data.get("organization_name") or org.get("organization_name") or "WebIntern").strip()
    website = (data.get("organization_website") or org.get("organization_website") or "www.webintern.in").strip()
    email = (data.get("organization_email") or org.get("organization_email") or "webinternsupport@gmail.com").strip()
    address = (data.get("organization_address") or org.get("organization_address") or "Virtual Learning Platform").strip()
    founder_name = (data.get("founder_name") or org.get("founder_name") or "Founding Board").strip()
    founder_desig = (data.get("founder_designation") or org.get("founder_designation") or "Founder").strip()
    td_name = (data.get("technical_director_name") or org.get("technical_director_name") or "Dr. A. K. Sharma").strip()
    td_desig = (data.get("technical_director_designation") or org.get("technical_director_designation") or "Technical Director").strip()

    execute_db("""
        INSERT INTO organization_settings (id, organization_name, organization_website, organization_email, organization_address, founder_name, founder_designation, technical_director_name, technical_director_designation)
        VALUES ('default', ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            organization_name=excluded.organization_name,
            organization_website=excluded.organization_website,
            organization_email=excluded.organization_email,
            organization_address=excluded.organization_address,
            founder_name=excluded.founder_name,
            founder_designation=excluded.founder_designation,
            technical_director_name=excluded.technical_director_name,
            technical_director_designation=excluded.technical_director_designation,
            updated_at=CURRENT_TIMESTAMP
    """, (name, website, email, address, founder_name, founder_desig, td_name, td_desig))

    return get_organization_settings()

def validate_master_record(data):
    errors = []
    
    # Required Fields
    student_name = (data.get("student_full_name") or "").strip()
    if not student_name:
        errors.append("Student Full Name is required.")
        
    college_name = (data.get("college_name") or "").strip()
    if not college_name:
        errors.append("College Name is required.")
        
    degree = (data.get("degree") or "").strip()
    if not degree:
        errors.append("Degree is required.")
        
    department = (data.get("department") or "").strip()
    if not department:
        errors.append("Department is required.")
        
    position = (data.get("internship_position") or "").strip()
    if not position:
        errors.append("Internship Position is required.")
        
    start_date = (data.get("internship_start_date") or "").strip()
    if not start_date:
        errors.append("Internship Start Date is required.")
        
    end_date = (data.get("internship_end_date") or "").strip()
    if not end_date:
        errors.append("Internship End Date is required.")
        
    project_title = (data.get("project_title") or "").strip()
    if not project_title:
        errors.append("Project Title is required.")
        
    mentor_name = (data.get("mentor_name") or "").strip()
    if not mentor_name:
        errors.append("Mentor Name is required.")

    # Date order validation
    if start_date and end_date:
        s_dt = parse_date_safely(start_date)
        e_dt = parse_date_safely(end_date)
        if s_dt and e_dt and s_dt > e_dt:
            errors.append("Internship Start Date cannot be after End Date.")

    # Email format validation
    student_email = (data.get("student_email") or "").strip()
    if student_email and not re.match(r"^[^@]+@[^@]+\.[^@]+$", student_email):
        errors.append("Invalid Student Email format.")

    return errors

def save_master_record(data, record_id=None):
    errors = validate_master_record(data)
    if errors:
        return None, errors

    start_date = format_date_human(data.get("internship_start_date"))
    end_date = format_date_human(data.get("internship_end_date"))
    duration = calculate_duration(start_date, end_date)

    # Process responsibilities array
    raw_resp = data.get("key_responsibilities", [])
    if isinstance(raw_resp, str):
        try:
            resp_list = json.loads(raw_resp)
        except Exception:
            resp_list = [r.strip() for r in raw_resp.split("\n") if r.strip()]
    else:
        resp_list = [str(r).strip() for r in raw_resp if str(r).strip()]
    if not resp_list:
        resp_list = [
            f"Develop and maintain {data.get('internship_position')} applications.",
            "Write, test and debug software components.",
            "Work with frontend and backend technologies.",
            "Participate in project development and testing.",
            "Document technical work and project progress."
        ]

    # Process learning outcomes array
    raw_outcomes = data.get("learning_outcomes", [])
    if isinstance(raw_outcomes, str):
        try:
            outcomes_list = json.loads(raw_outcomes)
        except Exception:
            outcomes_list = [o.strip() for o in raw_outcomes.split("\n") if o.strip()]
    else:
        outcomes_list = [str(o).strip() for o in raw_outcomes if str(o).strip()]
    if not outcomes_list:
        outcomes_list = [
            "Web Application Development",
            "Frontend Development",
            "Backend Development",
            "Database Management",
            "Software Testing"
        ]

    offer_date = format_date_human(data.get("offer_letter_issue_date") or start_date)
    cert_date = format_date_human(data.get("certificate_issue_date") or end_date)

    existing = query_db("SELECT * FROM master_internships WHERE id = ?", (record_id,), one=True) if record_id else None

    if existing:
        m_id = existing["id"]
        offer_id = existing["offer_id"]
        certificate_id = existing["certificate_id"]
        
        execute_db("""
            UPDATE master_internships SET
                student_full_name = ?, student_email = ?, student_mobile = ?, student_gender = ?, student_date_of_birth = ?, student_id = ?, roll_number = ?,
                college_name = ?, university_name = ?, degree = ?, department = ?, year_of_study = ?, semester = ?, academic_year = ?, college_location = ?,
                internship_domain = ?, internship_position = ?, internship_mode = ?, internship_start_date = ?, internship_end_date = ?, internship_duration = ?, internship_status = ?,
                project_title = ?, project_description = ?, technologies_used = ?, project_category = ?,
                key_responsibilities = ?, learning_outcomes = ?,
                mentor_name = ?, mentor_designation = ?, mentor_department = ?,
                offer_letter_issue_date = ?, certificate_issue_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            (data.get("student_full_name") or "").strip(),
            (data.get("student_email") or "").strip(),
            (data.get("student_mobile") or "").strip(),
            (data.get("student_gender") or "").strip(),
            (data.get("student_date_of_birth") or "").strip(),
            (data.get("student_id") or f"WI2026{(m_id[:6]).upper()}").strip(),
            (data.get("roll_number") or "").strip(),
            (data.get("college_name") or "").strip(),
            (data.get("university_name") or "").strip(),
            (data.get("degree") or "").strip(),
            (data.get("department") or "").strip(),
            (data.get("year_of_study") or "").strip(),
            (data.get("semester") or "").strip(),
            (data.get("academic_year") or "").strip(),
            (data.get("college_location") or "").strip(),
            (data.get("internship_domain") or data.get("internship_position") or "").strip(),
            (data.get("internship_position") or "").strip(),
            (data.get("internship_mode") or "Online").strip(),
            start_date,
            end_date,
            duration,
            (data.get("internship_status") or "Completed").strip(),
            (data.get("project_title") or "").strip(),
            (data.get("project_description") or "").strip(),
            (data.get("technologies_used") or "").strip(),
            (data.get("project_category") or "").strip(),
            json.dumps(resp_list),
            json.dumps(outcomes_list),
            (data.get("mentor_name") or "").strip(),
            (data.get("mentor_designation") or "Technical Mentor").strip(),
            (data.get("mentor_department") or "").strip(),
            offer_date,
            cert_date,
            m_id
        ))
    else:
        m_id = str(uuid.uuid4())
        offer_id = data.get("offer_id") or generate_unique_offer_id()
        certificate_id = data.get("certificate_id") or generate_unique_certificate_id()

        execute_db("""
            INSERT INTO master_internships (
                id, student_full_name, student_email, student_mobile, student_gender, student_date_of_birth, student_id, roll_number,
                college_name, university_name, degree, department, year_of_study, semester, academic_year, college_location,
                internship_domain, internship_position, internship_mode, internship_start_date, internship_end_date, internship_duration, internship_status,
                project_title, project_description, technologies_used, project_category,
                key_responsibilities, learning_outcomes,
                mentor_name, mentor_designation, mentor_department,
                offer_id, certificate_id, offer_letter_issue_date, certificate_issue_date, user_id, application_id
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?, ?, ?
            )
        """, (
            m_id,
            (data.get("student_full_name") or "").strip(),
            (data.get("student_email") or "").strip(),
            (data.get("student_mobile") or "").strip(),
            (data.get("student_gender") or "").strip(),
            (data.get("student_date_of_birth") or "").strip(),
            (data.get("student_id") or f"WI2026{(m_id[:6]).upper()}").strip(),
            (data.get("roll_number") or "").strip(),
            (data.get("college_name") or "").strip(),
            (data.get("university_name") or "").strip(),
            (data.get("degree") or "").strip(),
            (data.get("department") or "").strip(),
            (data.get("year_of_study") or "").strip(),
            (data.get("semester") or "").strip(),
            (data.get("academic_year") or "").strip(),
            (data.get("college_location") or "").strip(),
            (data.get("internship_domain") or data.get("internship_position") or "").strip(),
            (data.get("internship_position") or "").strip(),
            (data.get("internship_mode") or "Online").strip(),
            start_date,
            end_date,
            duration,
            (data.get("internship_status") or "Completed").strip(),
            (data.get("project_title") or "").strip(),
            (data.get("project_description") or "").strip(),
            (data.get("technologies_used") or "").strip(),
            (data.get("project_category") or "").strip(),
            json.dumps(resp_list),
            json.dumps(outcomes_list),
            (data.get("mentor_name") or "").strip(),
            (data.get("mentor_designation") or "Technical Mentor").strip(),
            (data.get("mentor_department") or "").strip(),
            offer_id,
            certificate_id,
            offer_date,
            cert_date,
            data.get("user_id"),
            data.get("application_id")
        ))

    rec = get_master_record(m_id)
    return rec, None

def get_master_record(record_id):
    rec = query_db("SELECT * FROM master_internships WHERE id = ? OR offer_id = ? OR certificate_id = ?", (record_id, record_id, record_id), one=True)
    if not rec:
        return None
    
    # Parse JSON lists
    try:
        rec["key_responsibilities"] = json.loads(rec["key_responsibilities"]) if rec.get("key_responsibilities") else []
    except Exception:
        rec["key_responsibilities"] = []

    try:
        rec["learning_outcomes"] = json.loads(rec["learning_outcomes"]) if rec.get("learning_outcomes") else []
    except Exception:
        rec["learning_outcomes"] = []

    return rec

def get_offer_letter_mapping(record):
    """Strictly map Master Record fields to Offer Letter fields without field fallback guessing."""
    org = get_organization_settings()
    
    return {
        "offer_id": record["offer_id"],
        "offer_letter_issue_date": record.get("offer_letter_issue_date") or record["internship_start_date"],
        "student_full_name": record["student_full_name"],
        "internship_position": record["internship_position"],
        "internship_start_date": record["internship_start_date"],
        "internship_end_date": record["internship_end_date"],
        "internship_duration": record["internship_duration"],
        "key_responsibilities": record.get("key_responsibilities") or [],
        "learning_outcomes": record.get("learning_outcomes") or [],
        "organization_name": org["organization_name"],
        "organization_website": org["organization_website"],
        "organization_email": org["organization_email"],
        "founder_name": org["founder_name"],
        "founder_designation": org["founder_designation"],
        "technical_director_name": org["technical_director_name"],
        "technical_director_designation": org["technical_director_designation"],
        "founder_signature": org["founder_signature"]
    }

def get_certificate_mapping(record):
    """Strictly map Master Record fields to Certificate fields without field fallback guessing."""
    org = get_organization_settings()
    
    return {
        "certificate_id": record["certificate_id"],
        "certificate_issue_date": record.get("certificate_issue_date") or record["internship_end_date"],
        "student_full_name": record["student_full_name"],
        "college_name": record["college_name"],
        "university_name": record.get("university_name") or "",
        "internship_position": record["internship_position"],
        "internship_start_date": record["internship_start_date"],
        "internship_end_date": record["internship_end_date"],
        "mentor_name": record["mentor_name"],
        "mentor_designation": record.get("mentor_designation") or "Technical Mentor",
        "project_title": record["project_title"],
        "organization_name": org["organization_name"],
        "founder_name": org["founder_name"],
        "founder_designation": org["founder_designation"]
    }

def save_document_snapshot(master_record_id, doc_type, doc_number, snapshot_dict, file_path):
    snap_id = str(uuid.uuid4())
    snap_json = json.dumps(snapshot_dict)
    
    execute_db("""
        INSERT INTO issued_snapshots (id, master_record_id, document_type, document_number, data_snapshot, file_path)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(document_number) DO UPDATE SET
            data_snapshot=excluded.data_snapshot,
            file_path=excluded.file_path,
            issued_at=CURRENT_TIMESTAMP
    """, (snap_id, master_record_id, doc_type, doc_number, snap_json, file_path))

    return snap_id
