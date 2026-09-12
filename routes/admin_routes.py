import uuid
from flask import Blueprint, jsonify, request
from database import query_db, execute_db
from utils.auth import admin_required

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    students_cnt = query_db("SELECT COUNT(*) as cnt FROM profiles", one=True)['cnt']
    apps_cnt = query_db("SELECT COUNT(*) as cnt FROM applications", one=True)['cnt']
    pending_reviews_cnt = query_db("SELECT COUNT(*) as cnt FROM submissions WHERE status = 'pending'", one=True)['cnt']
    certs_cnt = query_db("SELECT COUNT(*) as cnt FROM certificates", one=True)['cnt']
    
    rev_res = query_db("SELECT SUM(amount_inr) as total FROM payments WHERE status = 'paid'", one=True)
    total_revenue = rev_res['total'] if rev_res and rev_res['total'] else 0

    return jsonify({
        'stats': {
            'total_students': students_cnt,
            'total_applications': apps_cnt,
            'pending_reviews': pending_reviews_cnt,
            'issued_certificates': certs_cnt,
            'total_revenue_inr': total_revenue
        }
    }), 200

@admin_bp.route('/api/admin/submissions', methods=['GET'])
@admin_required
def get_admin_submissions():
    status_filter = request.args.get('status')
    
    sql = """
        SELECT s.*, a.user_id, p.full_name as student_name, p.email as student_email,
               i.title as internship_title, t.title as task_title, t.deliverables
        FROM submissions s
        JOIN applications a ON s.application_id = a.id
        JOIN profiles p ON a.user_id = p.id
        JOIN internships i ON a.internship_id = i.id
        LEFT JOIN internship_tasks t ON i.id = t.internship_id AND s.week_number = t.week_number
        WHERE 1=1
    """
    params = []
    if status_filter:
        sql += " AND s.status = ?"
        params.append(status_filter)
        
    sql += " ORDER BY s.submitted_at DESC"
    
    submissions = query_db(sql, params)
    return jsonify({'submissions': submissions}), 200

@admin_bp.route('/api/admin/applications', methods=['GET'])
@admin_required
def get_admin_applications():
    apps = query_db("""
        SELECT a.*, p.full_name as student_name, p.email as student_email, p.phone as student_phone,
               i.title as internship_title, s.name as sector_name
        FROM applications a
        JOIN profiles p ON a.user_id = p.id
        JOIN internships i ON a.internship_id = i.id
        JOIN sectors s ON i.sector_id = s.id
        ORDER BY a.applied_at DESC
    """)
    return jsonify({'applications': apps}), 200

@admin_bp.route('/api/admin/issue-certificate', methods=['POST'])
@admin_required
def issue_certificate_manually():
    data = request.get_json() or {}
    application_id = data.get('application_id')

    if not application_id:
        return jsonify({'error': 'Application ID is required.'}), 400

    app_record = query_db("SELECT * FROM applications WHERE id = ?", (application_id,), one=True)
    if not app_record:
        return jsonify({'error': 'Application record not found.'}), 404

    cert = query_db("SELECT * FROM certificates WHERE application_id = ?", (application_id,), one=True)
    if not cert:
        cert_id = str(uuid.uuid4())
        execute_db("INSERT INTO certificates (id, application_id, is_verified_paid) VALUES (?, ?, 0)", (cert_id, application_id))
    else:
        cert_id = cert['id']

    execute_db("UPDATE applications SET status = 'completed' WHERE id = ?", (application_id,))

    return jsonify({
        'message': 'Certificate issued successfully.',
        'certificate_id': cert_id
    }), 200

@admin_bp.route('/api/admin/google-sheets/status', methods=['GET'])
@admin_bp.route('/api/google-sheets/status', methods=['GET'])
def get_google_sheets_status():
    from utils.google_sheets_service import check_google_sheets_connection
    res = check_google_sheets_connection()
    return jsonify(res), 200

