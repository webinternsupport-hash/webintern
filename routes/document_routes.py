import os
import uuid
import datetime
from flask import Blueprint, request, jsonify, send_file, send_from_directory, Response
from database import query_db, execute_db
from utils.auth import jwt_required, admin_required
from utils.email_service import send_offer_letter_email, send_certificate_email
from utils.google_sheets_service import sync_offer_letter_to_google_sheets, sync_certificate_to_google_sheets
from utils.certificate_job import process_eligible_certificates
from config import Config

document_bp = Blueprint('document_bp', __name__)

@document_bp.route('/api/verify/<certificate_id>', methods=['GET'])
def verify_certificate(certificate_id):
    """Public certificate verification page & API endpoint (Section 29)."""
    clean_id = certificate_id.strip()

    # Query certificate and application database
    cert_record = query_db("""
        SELECT c.*, a.user_id, a.start_date, a.end_date, a.status as app_status,
               p.full_name as student_name, p.college as college_name,
               i.title as internship_title, i.company_name, i.guide_name, i.project_name
        FROM certificates c
        JOIN applications a ON c.application_id = a.id
        JOIN profiles p ON a.user_id = p.id
        JOIN internships i ON a.internship_id = i.id
        WHERE c.id = ? OR c.id LIKE ? OR a.certificate_id = ?
    """, (clean_id, f"%{clean_id}%", clean_id), one=True)

    if not cert_record:
        # Check document table fallback
        doc_record = query_db("SELECT * FROM documents WHERE document_number = ? AND document_type = 'CERTIFICATE'", (clean_id,), one=True)
        if doc_record:
            app_rec = query_db("""
                SELECT a.*, p.full_name as student_name, i.title as internship_title, i.company_name
                FROM applications a
                JOIN profiles p ON a.user_id = p.id
                JOIN internships i ON a.internship_id = i.id
                WHERE a.id = ?
            """, (doc_record['application_id'],), one=True)
            if app_rec:
                return jsonify({
                    'status': 'VERIFIED' if doc_record['status'] != 'REVOKED' else 'REVOKED',
                    'certificate_id': clean_id,
                    'student_name': app_rec['student_name'],
                    'internship_title': app_rec['internship_title'],
                    'company_name': app_rec.get('company_name') or 'Web Intern Platform',
                    'start_date': app_rec.get('start_date') or 'N/A',
                    'end_date': app_rec.get('end_date') or 'N/A',
                    'issue_date': doc_record.get('created_at', '')[:10] if doc_record.get('created_at') else 'N/A',
                    'document_status': doc_record['status']
                }), 200

        return jsonify({
            'status': 'INVALID',
            'error': 'Certificate ID not found in official WebIntern registry.',
            'certificate_id': clean_id
        }), 404

    is_revoked = cert_record.get('status') == 'REVOKED'
    issue_date_formatted = datetime.datetime.strptime(cert_record['issued_at'][:10], "%Y-%m-%d").strftime("%B %d, %Y") if cert_record.get('issued_at') else "N/A"

    return jsonify({
        'status': 'REVOKED' if is_revoked else 'VERIFIED',
        'certificate_id': cert_record.get('certificate_id') or cert_record['id'],
        'student_name': cert_record['student_name'],
        'college_name': cert_record.get('college_name') or "",
        'internship_title': cert_record['internship_title'],
        'company_name': cert_record.get('company_name') or 'Web Intern Platform',
        'guide_name': cert_record.get('guide_name') or 'Dr. A. K. Sharma',
        'project_name': cert_record.get('project_name') or f"{cert_record['internship_title']} Capstone",
        'start_date': cert_record.get('start_date') or 'N/A',
        'end_date': cert_record.get('end_date') or 'N/A',
        'issue_date': issue_date_formatted,
        'verification_url': f"https://webintern.in/verify/{clean_id}",
        'is_verified_paid': bool(cert_record.get('is_verified_paid'))
    }), 200

@document_bp.route('/api/documents/<doc_id>', methods=['GET'])
@jwt_required
def get_document_details(doc_id):
    user = request.user
    doc = query_db("SELECT * FROM documents WHERE id = ? OR document_number = ?", (doc_id, doc_id), one=True)
    
    if not doc:
        return jsonify({'error': 'Document record not found.'}), 404

    # Get application to verify ownership
    app = query_db("SELECT * FROM applications WHERE id = ?", (doc['application_id'],), one=True)
    if not app:
        return jsonify({'error': 'Associated application not found.'}), 404
    
    if user.get('role') != 'admin' and app['user_id'] != user['sub']:
        return jsonify({'error': 'Unauthorized access to document.'}), 403

    return jsonify({'document': doc}), 200

@document_bp.route('/api/documents/<doc_id>/download', methods=['GET'])
@jwt_required
def download_document(doc_id):
    user = request.user
    doc = query_db("SELECT * FROM documents WHERE id = ? OR document_number = ?", (doc_id, doc_id), one=True)
    if not doc:
        return jsonify({'error': 'Document not found.'}), 404

    # Check authorization - get the application and verify user ownership
    app = query_db("SELECT * FROM applications WHERE id = ?", (doc['application_id'],), one=True)
    if not app:
        return jsonify({'error': 'Associated application not found.'}), 404
    
    if user.get('role') != 'admin' and app['user_id'] != user['sub']:
        return jsonify({'error': 'Unauthorized access to document file.'}), 403

    file_path = doc['file_path']
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='application/pdf', as_attachment=True, download_name=f"{doc['document_number']}.pdf")
    
    # If file doesn't exist, regenerate it (offer letter)
    if doc['document_type'] == 'OFFER_LETTER':
        try:
            from utils.pdf_generator import generate_offer_letter_pdf
            internship = query_db("SELECT * FROM internships WHERE id = ?", (app['internship_id'],), one=True)
            profile = query_db("SELECT * FROM profiles WHERE id = ?", (app['user_id'],), one=True)
            
            if not internship or not profile:
                return jsonify({'error': 'Cannot regenerate offer letter - missing data.'}), 400
            
            pdf_bytes = generate_offer_letter_pdf(
                student_name=profile['full_name'],
                internship_title=internship['title'],
                date_str=app.get('start_date'),
                save_id=app['id'],
                company_name=internship.get('company_name') or "Web Intern Platform",
                start_date=app.get('start_date'),
                end_date=app.get('end_date'),
                duration=f"{internship.get('duration_weeks') or 4} Weeks",
                location=internship.get('location') or "Virtual / Remote",
                skills_tools=internship.get('skills_tools'),
                tasks_projects=internship.get('tasks_projects'),
                offer_id=doc['document_number'],
                college_name=profile.get('college'),
                department=profile.get('department')
            )
            return Response(
                pdf_bytes,
                mimetype='application/pdf',
                headers={'Content-Disposition': f'inline; filename="{doc["document_number"]}.pdf"'}
            )
        except Exception as e:
            print(f"[Offer Letter Regeneration Error]: {e}")
            return jsonify({'error': f'Document not found and regeneration failed: {str(e)}'}), 500
    
    return jsonify({'error': 'Document PDF file missing from disk.'}), 404

@document_bp.route('/api/students/<student_id>/documents', methods=['GET'])
@jwt_required
def get_student_documents(student_id):
    user = request.user
    if user.get('role') != 'admin' and user['sub'] != student_id:
        return jsonify({'error': 'Unauthorized.'}), 403

    docs = query_db("""
        SELECT d.*, i.title as internship_title, a.user_id as owner_id
        FROM documents d
        JOIN applications a ON d.application_id = a.id
        JOIN internships i ON a.internship_id = i.id
        WHERE a.user_id = ?
        ORDER BY d.created_at DESC
    """, (student_id,))

    return jsonify({'documents': docs}), 200

@document_bp.route('/api/documents/<doc_id>/revoke', methods=['POST'])
@admin_required
def revoke_document(doc_id):
    doc = query_db("SELECT * FROM documents WHERE id = ? OR document_number = ?", (doc_id, doc_id), one=True)
    if not doc:
        return jsonify({'error': 'Document not found.'}), 404

    execute_db("UPDATE documents SET status = 'REVOKED' WHERE id = ?", (doc['id'],))
    
    if doc['document_type'] == 'CERTIFICATE':
        execute_db("UPDATE certificates SET status = 'REVOKED' WHERE id = ? OR application_id = ?", (doc['document_number'], doc['application_id']))

    # Record audit log (Section 44)
    audit_id = str(uuid.uuid4())
    execute_db("""
        INSERT INTO audit_logs (id, user_id, student_id, document_id, document_type, action, ip_address, details)
        VALUES (?, ?, ?, ?, ?, 'REVOKED', ?, 'Document revoked by administrator')
    """, (audit_id, request.user['sub'], doc['student_id'], doc['id'], doc['document_type'], request.remote_addr))

    return jsonify({'message': f"Document {doc['document_number']} revoked successfully."}), 200

@document_bp.route('/api/admin/documents/<doc_id>/resend', methods=['POST'])
@admin_required
def resend_document_email(doc_id):
    doc = query_db("""
        SELECT d.*, p.full_name as student_name, p.email as student_email,
               a.start_date, a.end_date, i.title as internship_title, i.duration_weeks
        FROM documents d
        JOIN profiles p ON d.student_id = p.id
        JOIN applications a ON d.application_id = a.id
        JOIN internships i ON a.internship_id = i.id
        WHERE d.id = ? OR d.document_number = ?
    """, (doc_id, doc_id), one=True)

    if not doc:
        return jsonify({'error': 'Document record not found.'}), 404

    pdf_bytes = None
    if os.path.exists(doc['file_path']):
        with open(doc['file_path'], 'rb') as f:
            pdf_bytes = f.read()

    if doc['document_type'] == 'OFFER_LETTER':
        success, res = send_offer_letter_email(
            to_email=doc['student_email'],
            student_name=doc['student_name'],
            internship_title=doc['internship_title'],
            pdf_bytes=pdf_bytes,
            start_date=doc.get('start_date'),
            end_date=doc.get('end_date'),
            duration=f"{doc.get('duration_weeks') or 4} Weeks",
            offer_id=doc['document_number']
        )
    else:
        success, res = send_certificate_email(
            to_email=doc['student_email'],
            student_name=doc['student_name'],
            internship_title=doc['internship_title'],
            cert_id=doc['document_number'],
            pdf_bytes=pdf_bytes,
            start_date=doc.get('start_date'),
            end_date=doc.get('end_date'),
            verification_url=f"https://webintern.in/verify/{doc['document_number']}"
        )

    email_status = "SENT" if success else "FAILED"
    msg_id = res.get('id') if isinstance(res, dict) else str(res)
    execute_db("UPDATE documents SET email_status = ?, email_message_id = ? WHERE id = ?", (email_status, msg_id, doc['id']))

    return jsonify({'message': f"Document email re-sent successfully to {doc['student_email']}.", 'email_status': email_status}), 200

@document_bp.route('/api/admin/sheets/retry', methods=['POST'])
@admin_required
def retry_sheets_sync():
    """Retry failed Google Sheets synchronization records (Section 35 & 40)."""
    failed_docs = query_db("""
        SELECT d.*, p.full_name as student_name, p.email as student_email, p.phone as mobile, p.phone_country_code, p.college, p.department, p.degree,
               a.start_date, a.end_date, i.title as internship_title, i.company_name, i.guide_name, i.project_name
        FROM documents d
        JOIN profiles p ON d.student_id = p.id
        JOIN applications a ON d.application_id = a.id
        JOIN internships i ON a.internship_id = i.id
        WHERE d.sheets_synced = 0 OR d.sheets_synced IS NULL
    """)

    synced_count = 0
    for doc in failed_docs:
        if doc['document_type'] == 'OFFER_LETTER':
            sync_offer_letter_to_google_sheets({
                "offer_id": doc['document_number'],
                "student_id": doc['student_id'],
                "student_name": doc['student_name'],
                "email": doc['student_email'],
                "mobile": doc.get('mobile', ''),
                "phone_country_code": doc.get('phone_country_code', ''),
                "college": doc.get('college', ''),
                "department": doc.get('department', ''),
                "degree": doc.get('degree', ''),
                "course_name": doc['internship_title'],
                "role": doc['internship_title'],
                "company": doc.get('company_name') or "Web Intern Platform",
                "start_date": doc.get('start_date') or "",
                "end_date": doc.get('end_date') or "",
                "duration": "4 Weeks",
                "location": "Virtual / Remote",
                "issue_date": doc.get('created_at', '')[:10],
                "document_status": doc['status'],
                "email_status": doc['email_status'],
                "email_message_id": doc.get('email_message_id', '')
            }, document_id=doc['id'])
        else:
            sync_certificate_to_google_sheets({
                "certificate_id": doc['document_number'],
                "student_id": doc['student_id'],
                "student_name": doc['student_name'],
                "email": doc['student_email'],
                "mobile": doc.get('mobile', ''),
                "phone_country_code": doc.get('phone_country_code', ''),
                "college": doc.get('college', ''),
                "department": doc.get('department', ''),
                "degree": doc.get('degree', ''),
                "course_name": doc['internship_title'],
                "role": doc['internship_title'],
                "company": doc.get('company_name') or "Web Intern Platform",
                "start_date": doc.get('start_date') or "",
                "end_date": doc.get('end_date') or "",
                "duration": "4 Weeks",
                "guide_name": doc.get('guide_name') or "Dr. A. K. Sharma",
                "project_name": doc.get('project_name') or f"{doc['internship_title']} Capstone",
                "issue_date": doc.get('created_at', '')[:10],
                "document_status": doc['status'],
                "email_status": doc['email_status'],
                "email_message_id": doc.get('email_message_id', ''),
                "verification_url": f"https://webintern.in/verify/{doc['document_number']}"
            }, document_id=doc['id'])
        synced_count += 1

    return jsonify({'message': f"Triggered Google Sheets retry for {synced_count} records."}), 200

@document_bp.route('/api/admin/certificates/run-issuance-job', methods=['POST'])
@admin_required
def trigger_certificate_job():
    """Admin route to manually trigger background certificate automation job."""
    count = process_eligible_certificates()
    return jsonify({'message': f"Certificate automation job processed {count} eligible certificates.", 'issued_count': count}), 200
