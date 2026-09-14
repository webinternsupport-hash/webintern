import os
import uuid
import datetime
from flask import Blueprint, request, jsonify
from database import query_db, execute_db
from utils.auth import jwt_required, admin_required
from utils.razorpay_service import create_razorpay_order, verify_razorpay_signature
from utils.pdf_generator import generate_certificate_pdf
from utils.email_service import send_certificate_email
from utils.google_sheets_service import sync_certificate_to_google_sheets
from utils.supabase_sync import sync_payment_to_supabase, sync_certificate_to_supabase
from config import Config

payment_bp = Blueprint('payment_bp', __name__)

def _process_successful_certificate_payment(payment_rec):
    """
    Triggers certificate issuance, PDF generation, Resend email dispatch, and Google Sheets sync
    after verified payment of ₹199.
    """
    user_id = payment_rec['user_id']
    cert_id_param = payment_rec.get('certificate_id')

    # Fetch application/enrollment details
    app_rec = None
    if cert_id_param:
        app_rec = query_db("""
            SELECT a.*, i.title as internship_title, i.duration_weeks, i.company_name, i.guide_name, i.project_name,
                   p.full_name as student_name, p.email as student_email, p.phone as student_phone, p.phone_country_code,
                   p.college as student_college, p.department as student_dept, p.degree as student_degree
            FROM applications a
            JOIN internships i ON a.internship_id = i.id
            JOIN profiles p ON a.user_id = p.id
            WHERE a.id = ? OR a.certificate_id = ? OR a.user_id = ?
        """, (cert_id_param, cert_id_param, user_id), one=True)

    if not app_rec:
        app_rec = query_db("""
            SELECT a.*, i.title as internship_title, i.duration_weeks, i.company_name, i.guide_name, i.project_name,
                   p.full_name as student_name, p.email as student_email, p.phone as student_phone, p.phone_country_code,
                   p.college as student_college, p.department as student_dept, p.degree as student_degree
            FROM applications a
            JOIN internships i ON a.internship_id = i.id
            JOIN profiles p ON a.user_id = p.id
            WHERE a.user_id = ?
            ORDER BY a.applied_at DESC
        """, (user_id,), one=True)

    if not app_rec:
        print(f"[Payment Success Processing Warning]: No application found for user_id {user_id}")
        return False, "No enrollment found for user."

    app_id = app_rec['id']
    duration_weeks = app_rec.get('duration_weeks') or 4
    end_date_str = app_rec.get('end_date') or datetime.datetime.now().strftime("%B %d, %Y")
    cert_id = app_rec.get('certificate_id') or f"WI-INT-2026-{app_id[:6].upper()}"
    issue_date_str = datetime.datetime.now().strftime("%B %d, %Y")
    verify_url = f"https://webintern.in/verify/{cert_id}"

    # Generate Certificate PDF
    pdf_bytes = generate_certificate_pdf(
        student_name=app_rec['student_name'],
        internship_title=app_rec['internship_title'],
        date_str=issue_date_str,
        cert_id=cert_id,
        is_verified=True,
        college_name=app_rec.get('student_college'),
        guide_name=app_rec.get('guide_name') or "Dr. A. K. Sharma",
        project_name=app_rec.get('project_name') or f"{app_rec['internship_title']} Capstone",
        duration=f"{duration_weeks} Weeks",
        start_date=app_rec.get('start_date'),
        end_date=end_date_str,
        company_name=app_rec.get('company_name') or "Web Intern Platform",
        verification_url=verify_url
    )

    cert_file_path = os.path.join(Config.GENERATED_CERTIFICATES_DIR, f"certificate_{cert_id}.pdf")
    cert_url = f"/api/certificates/{cert_id}/pdf"

    # Upsert certificate record
    existing_cert = query_db("SELECT * FROM certificates WHERE application_id = ?", (app_id,), one=True)
    if existing_cert:
        execute_db("""
            UPDATE certificates
            SET certificate_url = ?, is_verified_paid = 1, issued_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (cert_url, existing_cert['id']))
        cert_db_id = existing_cert['id']
    else:
        cert_db_id = str(uuid.uuid4())
        execute_db("""
            INSERT INTO certificates (id, application_id, certificate_url, is_verified_paid)
            VALUES (?, ?, ?, 1)
        """, (cert_db_id, app_id, cert_url))
        
        # ✅ SYNC CERTIFICATE TO SUPABASE
        try:
            sync_certificate_to_supabase(user_id, app_id, {
                'certificate_url': cert_url,
                'certificate_number': cert_id,
                'is_verified': True,
                'issued_at': datetime.datetime.now().isoformat()
            })
        except Exception as e:
            print(f"[Supabase Sync Warning] Certificate sync failed: {e}")

    # Update application record
    execute_db("""
        UPDATE applications
        SET status = 'completed', completion_status = 'completed', certificate_id = ?
        WHERE id = ?
    """, (cert_id, app_id))

    # Update payment record with certificate_id
    execute_db("UPDATE payments SET certificate_id = ? WHERE id = ?", (cert_db_id, payment_rec['id']))

    # Send Resend Certificate Email
    email_success, email_res = send_certificate_email(
        to_email=app_rec['student_email'],
        student_name=app_rec['student_name'],
        internship_title=app_rec['internship_title'],
        cert_id=cert_id,
        pdf_bytes=pdf_bytes,
        start_date=app_rec.get('start_date'),
        end_date=end_date_str,
        verification_url=verify_url
    )

    email_status = "SENT" if email_success else "FAILED"
    msg_id = email_res.get('id') if isinstance(email_res, dict) else str(email_res)

    # Save document record if not existing
    doc_exists = query_db("SELECT * FROM documents WHERE application_id = ? AND document_type = 'CERTIFICATE'", (app_id,), one=True)
    if doc_exists:
        execute_db("""
            UPDATE documents
            SET status = 'ISSUED', email_status = ?, email_message_id = ?, file_path = ?
            WHERE id = ?
        """, (email_status, msg_id, cert_file_path, doc_exists['id']))
        doc_id = doc_exists['id']
    else:
        doc_id = str(uuid.uuid4())
        execute_db("""
            INSERT INTO documents (id, application_id, student_id, document_type, document_number, file_path, status, email_status, email_message_id)
            VALUES (?, ?, ?, 'CERTIFICATE', ?, ?, 'ISSUED', ?, ?)
        """, (doc_id, app_id, app_rec['user_id'], cert_id, cert_file_path, email_status, msg_id))

    # Sync to Google Sheets
    sync_certificate_to_google_sheets({
        "certificate_id": cert_id,
        "student_id": app_rec['user_id'],
        "student_name": app_rec['student_name'],
        "email": app_rec['student_email'],
        "mobile": app_rec.get('student_phone') or "",
        "phone_country_code": app_rec.get('phone_country_code') or "",
        "college": app_rec.get('student_college') or "",
        "department": app_rec.get('student_dept') or "",
        "degree": app_rec.get('student_degree') or "",
        "course_name": app_rec['internship_title'],
        "role": app_rec['internship_title'],
        "company": app_rec.get('company_name') or "Web Intern Platform",
        "start_date": app_rec.get('start_date') or "",
        "end_date": end_date_str or "",
        "duration": f"{duration_weeks} Weeks",
        "guide_name": app_rec.get('guide_name') or "Dr. A. K. Sharma",
        "project_name": app_rec.get('project_name') or f"{app_rec['internship_title']} Capstone",
        "issue_date": issue_date_str,
        "document_status": "ISSUED",
        "email_status": email_status,
        "email_message_id": msg_id,
        "verification_url": verify_url
    }, document_id=doc_id)

    print(f"[Payment Verification Success]: Certificate {cert_id} generated & issued to {app_rec['student_name']} ({app_rec['student_email']})")
    return True, cert_id

@payment_bp.route('/api/payments/create-order', methods=['POST'])
@payment_bp.route('/api/payments/certificate/create-order', methods=['POST'])
@jwt_required
def create_order():
    user = request.user
    data = request.get_json() or {}
    certificate_id = data.get('certificate_id')
    enrollment_id = data.get('enrollment_id') or data.get('application_id')

    # Verify student enrollment eligibility before creating Razorpay order (PDF Rule 5)
    app_rec = None
    if enrollment_id:
        app_rec = query_db("SELECT * FROM applications WHERE id = ? AND user_id = ?", (enrollment_id, user['sub']), one=True)
    elif certificate_id:
        cert_rec = query_db("SELECT * FROM certificates WHERE id = ?", (certificate_id,), one=True)
        if cert_rec:
            app_rec = query_db("SELECT * FROM applications WHERE id = ? AND user_id = ?", (cert_rec['application_id'], user['sub']), one=True)

    if not app_rec:
        app_rec = query_db("SELECT * FROM applications WHERE user_id = ? ORDER BY applied_at DESC", (user['sub'],), one=True)

    if not app_rec:
        return jsonify({'error': 'No eligible enrollment found for this user.'}), 404

    # Fixed certificate fee: ₹199 INR (19900 paise)
    amount_inr = Config.CERTIFICATE_PRICE_INR

    # Check if user has an existing order or paid certificate
    existing_paid = query_db("""
        SELECT * FROM payments
        WHERE user_id = ? AND status = 'paid'
          AND (certificate_id = ? OR user_id = ?)
    """, (user['sub'], certificate_id, user['sub']), one=True)

    if existing_paid:
        return jsonify({
            'message': 'Certificate has already been paid for.',
            'status': 'PAID',
            'already_paid': True
        }), 200

    receipt_id = f"rcpt_{uuid.uuid4().hex[:10]}"
    success, razorpay_order = create_razorpay_order(
        amount_inr,
        receipt_id,
        notes={'certificate_id': certificate_id or app_rec['id'], 'user_id': user['sub']}
    )

    if not success:
        return jsonify({'error': 'Failed to create payment order with Razorpay gateway.'}), 500

    order_id = razorpay_order['id']

    # Store payment record in database
    payment_id = str(uuid.uuid4())
    execute_db("""
        INSERT INTO payments (id, user_id, certificate_id, razorpay_order_id, amount_inr, status)
        VALUES (?, ?, ?, ?, ?, 'created')
    """, (payment_id, user['sub'], certificate_id or app_rec['id'], order_id, amount_inr))

    return jsonify({
        'message': 'Razorpay order generated successfully for ₹199 Certificate Fee.',
        'order_id': order_id,
        'key_id': Config.RAZORPAY_KEY_ID,
        'amount': razorpay_order['amount'],
        'currency': razorpay_order['currency'],
        'payment_record_id': payment_id,
        'certificate_fee_inr': amount_inr
    }), 200

@payment_bp.route('/api/payments/verify', methods=['POST'])
@payment_bp.route('/api/payments/certificate/verify', methods=['POST'])
@jwt_required
def verify_payment():
    user = request.user
    data = request.get_json() or {}
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')

    if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
        return jsonify({'error': 'Missing payment signature verification parameters.'}), 400

    is_valid = verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)
    if not is_valid:
        return jsonify({'error': 'Payment signature verification failed.'}), 400

    # Fetch and update payment record
    pmt = query_db("SELECT * FROM payments WHERE razorpay_order_id = ?", (razorpay_order_id,), one=True)
    if not pmt:
        # Create payment record if created via frontend Razorpay popup directly
        payment_id = str(uuid.uuid4())
        execute_db("""
            INSERT INTO payments (id, user_id, razorpay_order_id, razorpay_payment_id, razorpay_signature, amount_inr, status)
            VALUES (?, ?, ?, ?, ?, ?, 'paid')
        """, (payment_id, user['sub'], razorpay_order_id, razorpay_payment_id, razorpay_signature, Config.CERTIFICATE_PRICE_INR))
        pmt = query_db("SELECT * FROM payments WHERE id = ?", (payment_id,), one=True)
    else:
        execute_db("""
            UPDATE payments
            SET razorpay_payment_id = ?, razorpay_signature = ?, status = 'paid'
            WHERE razorpay_order_id = ?
        """, (razorpay_payment_id, razorpay_signature, razorpay_order_id))
        pmt = query_db("SELECT * FROM payments WHERE id = ?", (pmt['id'],), one=True)

    # ✅ SYNC PAYMENT TO SUPABASE
    try:
        # Get application to link application_id
        app_rec = query_db("SELECT id FROM applications WHERE user_id = ? ORDER BY applied_at DESC LIMIT 1", (user['sub'],), one=True)
        if app_rec:
            sync_payment_to_supabase(user['sub'], app_rec['id'], {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
                'amount_inr': pmt['amount_inr'],
                'status': 'paid'
            })
    except Exception as e:
        print(f"[Supabase Sync Warning] Payment sync failed: {e}")

    # Trigger Certificate generation, PDF save, Resend email dispatch & Google Sheets sync
    succ, cert_info = _process_successful_certificate_payment(pmt)

    return jsonify({
        'message': 'Payment verified successfully! Your Internship Completion Certificate has been released and emailed.',
        'status': 'paid',
        'certificate_issued': succ,
        'certificate_id': cert_info if succ else None
    }), 200

@payment_bp.route('/api/payments/razorpay/webhook', methods=['POST'])
@payment_bp.route('/api/payments/webhook', methods=['POST'])
def payment_webhook():
    payload = request.get_data(as_text=True)
    signature = request.headers.get('X-Razorpay-Signature')

    data = request.get_json() or {}
    event = data.get('event')
    print(f"[Razorpay Webhook Event Received]: {event}")

    if event == 'payment.captured':
        payment_entity = data.get('payload', {}).get('payment', {}).get('entity', {})
        order_id = payment_entity.get('order_id')
        payment_id = payment_entity.get('id')

        if order_id:
            execute_db("UPDATE payments SET status = 'paid', razorpay_payment_id = ? WHERE razorpay_order_id = ?", (payment_id, order_id))
            pmt = query_db("SELECT * FROM payments WHERE razorpay_order_id = ?", (order_id,), one=True)
            if pmt:
                _process_successful_certificate_payment(pmt)

    return jsonify({'status': 'ok'}), 200

@payment_bp.route('/api/payments/certificate/status/<enrollment_id>', methods=['GET'])
@jwt_required
def get_certificate_payment_status(enrollment_id):
    user = request.user
    app_rec = query_db("SELECT * FROM applications WHERE id = ? OR certificate_id = ?", (enrollment_id, enrollment_id), one=True)
    if not app_rec:
        return jsonify({'error': 'Enrollment not found.'}), 404

    pmt = query_db("SELECT * FROM payments WHERE user_id = ? AND status = 'paid'", (user['sub'],), one=True)
    cert = query_db("SELECT * FROM certificates WHERE application_id = ?", (app_rec['id'],), one=True)

    paid = bool(pmt or (cert and cert.get('is_verified_paid')))

    return jsonify({
        'enrollment_id': app_rec['id'],
        'completion_status': app_rec.get('completion_status'),
        'certificate_id': app_rec.get('certificate_id'),
        'is_paid': paid,
        'certificate_fee_inr': Config.CERTIFICATE_PRICE_INR,
        'status': 'PAYMENT_PAID' if paid else ('READY_FOR_PAYMENT' if app_rec.get('completion_status') in ['eligible', 'completed'] else 'NOT_ELIGIBLE')
    }), 200

@payment_bp.route('/api/payments/<payment_id>', methods=['GET'])
@jwt_required
def get_payment_details(payment_id):
    user = request.user
    pmt = query_db("SELECT * FROM payments WHERE id = ? OR razorpay_order_id = ? OR razorpay_payment_id = ?", (payment_id, payment_id, payment_id), one=True)
    if not pmt:
        return jsonify({'error': 'Payment record not found.'}), 404

    if user.get('role') != 'admin' and pmt['user_id'] != user['sub']:
        return jsonify({'error': 'Unauthorized.'}), 403

    return jsonify({'payment': pmt}), 200

@payment_bp.route('/api/admin/payments/<payment_id>/resend-certificate', methods=['POST'])
@payment_bp.route('/api/admin/payments/<payment_id>/retry-email', methods=['POST'])
@admin_required
def admin_resend_certificate_email(payment_id):
    pmt = query_db("SELECT * FROM payments WHERE id = ?", (payment_id,), one=True)
    if not pmt:
        return jsonify({'error': 'Payment record not found.'}), 404

    succ, cert_info = _process_successful_certificate_payment(pmt)
    return jsonify({
        'message': f"Resent certificate email for payment {payment_id}.",
        'success': succ,
        'certificate_id': cert_info
    }), 200

@payment_bp.route('/api/payments/me', methods=['GET'])
@payment_bp.route('/api/payments/history', methods=['GET'])
@jwt_required
def get_my_payment_history():
    """Get payment and transaction history for the logged-in student."""
    user = request.user
    user_email = user.get('email', '')
    
    # Fetch all payments for this user
    payments = query_db("""
        SELECT p.*, 
               a.id as application_id,
               i.title as internship_title,
               i.slug as internship_slug,
               c.id as certificate_id,
               c.certificate_url
        FROM payments p
        LEFT JOIN applications a ON p.certificate_id = a.certificate_id OR p.certificate_id = a.id
        LEFT JOIN internships i ON a.internship_id = i.id
        LEFT JOIN certificates c ON a.id = c.application_id
        WHERE p.user_id = ? OR p.user_id IN (SELECT id FROM profiles WHERE LOWER(email) = LOWER(?))
        ORDER BY p.created_at DESC
    """, (user['sub'], user_email)) or []
    
    # Format response
    payment_history = []
    for pmt in payments:
        payment_history.append({
            'id': pmt['id'],
            'order_id': pmt.get('razorpay_order_id'),
            'payment_id': pmt.get('razorpay_payment_id'),
            'amount_inr': pmt.get('amount_inr'),
            'status': pmt.get('status'),
            'certificate_fee': pmt.get('amount_inr'),
            'application_id': pmt.get('application_id'),
            'certificate_id': pmt.get('certificate_id'),
            'internship_title': pmt.get('internship_title'),
            'internship_slug': pmt.get('internship_slug'),
            'certificate_url': pmt.get('certificate_url'),
            'created_at': pmt.get('created_at'),
            'paid_at': pmt.get('paid_at'),
            'transaction_date': pmt.get('created_at'),
            'description': f"Certificate Fee - {pmt.get('internship_title', 'Certificate')}"
        })
    
    return jsonify({
        'payments': payment_history,
        'transactions': payment_history,
        'total_paid': sum([p['amount_inr'] for p in payment_history if p['status'] == 'paid']),
        'total_transactions': len(payment_history)
    }), 200
