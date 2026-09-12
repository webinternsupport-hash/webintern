import datetime
from flask import Blueprint, jsonify, Response, render_template_string
from database import query_db
from utils.pdf_generator import generate_certificate_pdf

certificate_bp = Blueprint('certificate_bp', __name__)

CERTIFICATE_NOT_RELEASED_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Certificate Payment Required — WEBINTERN</title>
  <style>
    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background-color: #0F172A;
      color: #F8FAFC;
      margin: 0;
      padding: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }
    .card {
      background-color: #1E293B;
      border: 1px solid #334155;
      border-radius: 16px;
      padding: 40px;
      max-width: 520px;
      text-align: center;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .logo {
      font-size: 28px;
      font-weight: 800;
      color: #38BDF8;
      margin-bottom: 20px;
    }
    h2 {
      font-size: 22px;
      color: #FFFFFF;
      margin-top: 0;
    }
    p {
      color: #94A3B8;
      font-size: 15px;
      line-height: 1.6;
      margin-bottom: 24px;
    }
    .badge {
      display: inline-block;
      background-color: #FEF3C7;
      color: #92400E;
      font-weight: 700;
      font-size: 13px;
      padding: 6px 16px;
      border-radius: 99px;
      margin-bottom: 20px;
    }
    .btn {
      display: inline-block;
      background-color: #0B3D91;
      color: #FFFFFF;
      text-decoration: none;
      font-weight: 600;
      font-size: 15px;
      padding: 12px 28px;
      border-radius: 99px;
      transition: background-color 0.2s ease;
    }
    .btn:hover {
      background-color: #1D4ED8;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">web<span style="color: #38BDF8;">intern</span></div>
    <div class="badge">💳 ₹199 Certificate Fee & Completion Required</div>
    <h2>Internship Certificate Not Released Yet</h2>
    <p>
      This Internship Completion Certificate requires completion of the 4-week module tasks and verification of the <strong>₹199 Certificate Fee</strong>.
    </p>
    <a href="/#/dashboard" class="btn">Go to Dashboard to Pay & Release →</a>
  </div>
</body>
</html>
"""

CERTIFICATE_ASSIGNMENT_PENDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Payment Verified — Assignments Pending — WEBINTERN</title>
  <style>
    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background-color: #0F172A;
      color: #F8FAFC;
      margin: 0;
      padding: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }
    .card {
      background-color: #1E293B;
      border: 1px solid #334155;
      border-radius: 16px;
      padding: 40px;
      max-width: 540px;
      text-align: center;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .logo {
      font-size: 28px;
      font-weight: 800;
      color: #38BDF8;
      margin-bottom: 20px;
    }
    h2 {
      font-size: 22px;
      color: #FFFFFF;
      margin-top: 0;
    }
    p {
      color: #94A3B8;
      font-size: 15px;
      line-height: 1.6;
      margin-bottom: 24px;
    }
    .badge {
      display: inline-block;
      background-color: #D1FAE5;
      color: #065F46;
      font-weight: 700;
      font-size: 13px;
      padding: 6px 16px;
      border-radius: 99px;
      margin-bottom: 20px;
    }
    .btn {
      display: inline-block;
      background-color: #0B3D91;
      color: #FFFFFF;
      text-decoration: none;
      font-weight: 600;
      font-size: 15px;
      padding: 12px 28px;
      border-radius: 99px;
      transition: background-color 0.2s ease;
    }
    .btn:hover {
      background-color: #1D4ED8;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">web<span style="color: #38BDF8;">intern</span></div>
    <div class="badge">✅ Payment Verified — 4-Week Tasks Pending</div>
    <h2>Payment Received Successfully!</h2>
    <p>
      Your certificate payment of <strong>₹199</strong> has been verified. To maintain academic and industry standards, your official Certificate will be automatically issued and emailed to your inbox upon completing all <strong>4 weeks of internship assignments</strong>.
    </p>
    <a href="/#/dashboard" class="btn">Go to Dashboard & Complete Assignments →</a>
  </div>
</body>
</html>
"""

def _is_app_completed(app_id):
    app_rec = query_db("SELECT status, completion_status FROM applications WHERE id = ?", (app_id,), one=True)
    if not app_rec:
        return False
    if app_rec.get('status') == 'completed' or app_rec.get('completion_status') == 'completed':
        return True
    approved_cnt = query_db("SELECT COUNT(*) as cnt FROM submissions WHERE application_id = ? AND status IN ('approved', 'graded')", (app_id,), one=True)
    return bool(approved_cnt and approved_cnt['cnt'] >= 4)

@certificate_bp.route('/api/certificates/<cert_id>', methods=['GET'])
@certificate_bp.route('/certificates/<cert_id>', methods=['GET'])
def get_certificate(cert_id):
    clean_id = str(cert_id).strip()
    cert = query_db("""
        SELECT c.*, a.user_id, a.applied_at, p.full_name as student_name,
               i.title as internship_title, s.name as sector_name
        FROM certificates c
        JOIN applications a ON c.application_id = a.id
        JOIN profiles p ON a.user_id = p.id
        JOIN internships i ON a.internship_id = i.id
        JOIN sectors s ON i.sector_id = s.id
        WHERE c.id = ? OR c.application_id = ? OR a.certificate_id = ? OR a.id = ?
    """, (clean_id, clean_id, clean_id, clean_id), one=True)

    if not cert:
        return jsonify({'error': 'Certificate record not found.'}), 404

    return jsonify({'certificate': cert}), 200

@certificate_bp.route('/api/certificates/<cert_id>/pdf', methods=['GET'])
@certificate_bp.route('/certificates/<cert_id>/pdf', methods=['GET'])
def download_certificate_pdf(cert_id):
    clean_id = str(cert_id).strip()
    cert = query_db("""
        SELECT c.*, a.id as application_id, a.user_id, a.status as app_status, a.completion_status as app_completion_status, a.end_date, a.start_date, 
               p.full_name as student_name, p.college as student_college, p.department as student_dept,
               m.college_name as master_college, m.department as master_dept,
               i.title as internship_title, i.company_name, i.guide_name, i.project_name
        FROM certificates c
        JOIN applications a ON c.application_id = a.id
        JOIN profiles p ON a.user_id = p.id
        LEFT JOIN internships i ON a.internship_id = i.id
        LEFT JOIN master_internships m ON a.id = m.application_id
        WHERE c.id = ? OR c.application_id = ? OR a.certificate_id = ? OR a.id = ?
    """, (clean_id, clean_id, clean_id, clean_id), one=True)

    if not cert:
        # Check applications directly with LEFT JOIN to handle missing internships
        app_rec = query_db("""
            SELECT a.*, p.full_name as student_name, p.college as student_college, p.department as student_dept,
                   m.college_name as master_college, m.department as master_dept,
                   COALESCE(i.title, 'Virtual Internship') as internship_title, 
                   COALESCE(i.company_name, 'Web Intern Platform') as company_name, 
                   COALESCE(i.guide_name, 'Dr. A. K. Sharma') as guide_name, 
                   COALESCE(i.project_name, 'Capstone Project') as project_name
            FROM applications a
            JOIN profiles p ON a.user_id = p.id
            LEFT JOIN internships i ON a.internship_id = i.id
            LEFT JOIN master_internships m ON a.id = m.application_id
            WHERE a.id = ? OR a.certificate_id = ? OR a.certificate_id LIKE ?
        """, (clean_id, clean_id, f"%{clean_id}%"), one=True)

        if not app_rec:
            return render_template_string(CERTIFICATE_NOT_RELEASED_HTML), 404

        # Check payment status
        pmt = query_db("""
            SELECT * FROM payments 
            WHERE user_id = ? AND (certificate_id = ? OR certificate_id = ? OR certificate_id = ?) AND status = 'paid'
        """, (app_rec['user_id'], app_rec['id'], app_rec.get('certificate_id'), clean_id), one=True)

        if not pmt:
            return render_template_string(CERTIFICATE_NOT_RELEASED_HTML), 402

        # Check 4-week task completion status
        if not _is_app_completed(app_rec['id']):
            return render_template_string(CERTIFICATE_ASSIGNMENT_PENDING_HTML), 403

        date_str = datetime.datetime.now().strftime("%B %d, %Y")
        cert_id_str = app_rec.get('certificate_id') or f"WI-INT-2026-{app_rec['id'][:6].upper()}"
        eff_college = app_rec.get('master_college') or app_rec.get('student_college')
        eff_dept = app_rec.get('master_dept') or app_rec.get('student_dept')

        pdf_bytes = generate_certificate_pdf(
            student_name=app_rec['student_name'],
            internship_title=app_rec['internship_title'],
            date_str=date_str,
            cert_id=cert_id_str,
            is_verified=True,
            college_name=eff_college,
            department=eff_dept,
            guide_name=app_rec.get('guide_name') or "Dr. A. K. Sharma",
            project_name=app_rec.get('project_name') or f"{app_rec['internship_title']} Capstone",
            start_date=app_rec.get('start_date'),
            end_date=app_rec.get('end_date'),
            company_name=app_rec.get('company_name') or "Web Intern Platform"
        )
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'inline; filename="WebIntern_Certificate_{cert_id_str}.pdf"'}
        )

    # Check payment status on certificate record
    is_paid = bool(cert.get('is_verified_paid'))
    if not is_paid:
        pmt = query_db("""
            SELECT * FROM payments 
            WHERE user_id = ? AND (certificate_id = ? OR certificate_id = ? OR certificate_id = ?) AND status = 'paid'
        """, (cert['user_id'], cert['id'], cert.get('application_id'), clean_id), one=True)
        if pmt:
            is_paid = True
            from database import execute_db
            execute_db("UPDATE certificates SET is_verified_paid = 1 WHERE id = ?", (cert['id'],))

    if not is_paid:
        return render_template_string(CERTIFICATE_NOT_RELEASED_HTML), 402

    # Check 4-week task completion status
    if not _is_app_completed(cert['application_id']):
        return render_template_string(CERTIFICATE_ASSIGNMENT_PENDING_HTML), 403

    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    cert_id_str = cert.get('certificate_id') or cert['id']
    eff_college = cert.get('master_college') or cert.get('student_college') or 'Institution'
    eff_dept = cert.get('master_dept') or cert.get('student_dept') or 'Department'

    pdf_bytes = generate_certificate_pdf(
        student_name=cert['student_name'],
        internship_title=cert.get('internship_title') or 'Virtual Internship',
        date_str=date_str,
        cert_id=cert_id_str,
        is_verified=True,
        college_name=eff_college,
        department=eff_dept,
        guide_name=cert.get('guide_name') or "Dr. A. K. Sharma",
        project_name=cert.get('project_name') or f"{cert.get('internship_title', 'Internship')} Capstone",
        start_date=cert.get('start_date'),
        end_date=cert.get('end_date'),
        company_name=cert.get('company_name') or "Web Intern Platform"
    )

    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'inline; filename="WebIntern_Certificate_{cert_id_str}.pdf"'}
    )

@certificate_bp.route('/api/certificates/<cert_id>/send-email', methods=['POST'])
def send_certificate_email_route(cert_id):
    clean_id = str(cert_id).strip()
    cert = query_db("""
        SELECT c.*, a.user_id, a.end_date, a.start_date, p.full_name as student_name, p.email as student_email, p.college as student_college, p.department as student_dept,
               m.college_name as master_college, m.department as master_dept,
               i.title as internship_title, i.company_name, i.guide_name, i.project_name
        FROM certificates c
        JOIN applications a ON c.application_id = a.id
        JOIN profiles p ON a.user_id = p.id
        JOIN internships i ON a.internship_id = i.id
        LEFT JOIN master_internships m ON a.id = m.application_id
        WHERE c.id = ? OR c.application_id = ? OR a.certificate_id = ? OR a.id = ?
    """, (clean_id, clean_id, clean_id, clean_id), one=True)

    if not cert:
        return jsonify({'error': 'Certificate record not found.'}), 404

    is_paid = bool(cert.get('is_verified_paid'))
    if not is_paid:
        pmt = query_db("""
            SELECT * FROM payments 
            WHERE user_id = ? AND (certificate_id = ? OR certificate_id = ? OR certificate_id = ?) AND status = 'paid'
        """, (cert['user_id'], cert['id'], cert.get('application_id'), clean_id), one=True)
        if pmt:
            is_paid = True

    if not is_paid:
        return jsonify({'error': 'Payment of ₹199 is required before emailing certificate.'}), 402

    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    cert_id_str = cert.get('certificate_id') or cert['id']
    eff_college = cert.get('master_college') or cert.get('student_college')
    eff_dept = cert.get('master_dept') or cert.get('student_dept')
    verify_url = f"https://webintern.in/verify/{cert_id_str}"

    pdf_bytes = generate_certificate_pdf(
        student_name=cert['student_name'],
        internship_title=cert['internship_title'],
        date_str=date_str,
        cert_id=cert_id_str,
        is_verified=True,
        college_name=eff_college,
        department=eff_dept,
        guide_name=cert.get('guide_name') or "Dr. A. K. Sharma",
        project_name=cert.get('project_name') or f"{cert['internship_title']} Capstone",
        start_date=cert.get('start_date'),
        end_date=cert.get('end_date'),
        company_name=cert.get('company_name') or "Web Intern Platform",
        verification_url=verify_url
    )

    from utils.email_service import send_certificate_email
    email_ok, email_res = send_certificate_email(
        to_email=cert['student_email'],
        student_name=cert['student_name'],
        internship_title=cert['internship_title'],
        cert_id=cert_id_str,
        pdf_bytes=pdf_bytes,
        start_date=cert.get('start_date'),
        end_date=cert.get('end_date'),
        verification_url=verify_url
    )

    return jsonify({
        'message': f'Certificate PDF emailed successfully to {cert["student_email"]}',
        'email_sent': email_ok,
        'email_data': email_res
    }), 200

