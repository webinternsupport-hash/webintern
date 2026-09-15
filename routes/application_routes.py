import uuid
import datetime
import os
from flask import Blueprint, request, jsonify, Response, send_file
import threading
from database import query_db, execute_db
from utils.auth import jwt_required, relink_user_data_by_email
from utils.email_service import send_offer_letter_email
from utils.pdf_generator import generate_offer_letter_pdf
from utils.google_sheets_service import sync_offer_letter_to_google_sheets
from utils.supabase_sync import sync_enrollment_to_supabase
from config import Config

application_bp = Blueprint('application_bp', __name__)

@application_bp.route('/api/applications', methods=['POST'])
@application_bp.route('/applications', methods=['POST'])
@application_bp.route('/api/enrollments', methods=['POST'])
@application_bp.route('/enrollments', methods=['POST'])
@jwt_required
def create_application():
    try:
        user = request.user
        data = request.get_json() or {}
        internship_id = data.get('internship_id') or data.get('course_id')

        warnings = []

        if not internship_id:
            return jsonify({'error': 'Internship / Course ID is required.'}), 400

        internship = query_db("SELECT * FROM internships WHERE id = ?", (internship_id,), one=True)
        if not internship:
            return jsonify({'error': 'Selected internship program not found.'}), 404

        existing = query_db("SELECT * FROM applications WHERE user_id = ? AND internship_id = ?", (user['sub'], internship_id), one=True)
        if existing:
            print(f"[Application Already Exists] User: {user['sub']}, Internship: {internship_id}, App ID: {existing['id']}")
            return jsonify({
                'message': 'You have already applied to / enrolled in this internship.',
                'application': existing,
                'enrollment': existing,
                'warnings': []
            }), 200

        app_id = str(uuid.uuid4())
        now_dt = datetime.datetime.now()
        start_date_str = now_dt.strftime("%B %d, %Y")
        duration_weeks = internship.get('duration_weeks') or 4
        end_dt = now_dt + datetime.timedelta(weeks=duration_weeks)
        end_date_str = end_dt.strftime("%B %d, %Y")

        offer_id = f"WI-OFFER-2026-{app_id[:6].upper()}"
        cert_id = f"WI-CERT-2026-{app_id[:6].upper()}"

        # ================================================
        # 1) SAVE APPLICATION (CORE) - MUST SUCCEED
        # ================================================
        try:
            execute_db("""
                INSERT INTO applications (id, user_id, internship_id, status, offer_letter_sent, start_date, end_date, offer_letter_id, certificate_id, completion_status, applied_at)
                VALUES (?, ?, ?, 'active', 1, ?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)
            """, (app_id, user['sub'], internship_id, start_date_str, end_date_str, offer_id, cert_id))
            print(f"[Application Created] ID: {app_id}, User: {user['sub']}, Internship: {internship_id}")
        except Exception as e:
            print(f"[Application Creation CRITICAL ERROR] {e}")
            if 'UNIQUE constraint' in str(e):
                return jsonify({'error': 'You have already applied for this internship.'}), 400
            elif 'FOREIGN KEY constraint' in str(e):
                return jsonify({'error': 'Invalid internship selected. Please try again.'}), 400
            else:
                return jsonify({'error': 'Failed to save application. Please refresh the page and try again.'}), 500

        # ================================================
        # 2) SYNC TO SUPABASE (OPTIONAL)
        # ================================================
        try:
            sync_enrollment_to_supabase(user['sub'], {
                'internship_id': internship_id,
                'status': 'active',
                'start_date': start_date_str,
                'end_date': end_date_str,
                'offer_letter_id': offer_id,
                'certificate_id': cert_id
            })
        except Exception as e:
            print(f"[Supabase Sync Warning] {e}")
            warnings.append("Cloud sync not available; enrollment saved locally.")

        # ================================================
        # 3) LOAD PROFILE DEFAULTS
        # ================================================
        try:
            profile = query_db("SELECT * FROM profiles WHERE id = ?", (user['sub'],), one=True)
        except Exception as e:
            print(f"[Profile Load Warning] {e}")
            profile = None
            warnings.append("Could not read your profile; using default values on documents.")

        student_name = (profile.get('full_name') if profile else None) or user.get('name') or "Student Candidate"
        to_email = (profile.get('email') if profile else None) or user.get('email') or ""
        student_mobile = (profile.get('phone') or profile.get('mobile') or "") if profile else ""
        student_college = (profile.get('college') or data.get('college') or data.get('college_name') or "Recognized College / Institution") if profile else (data.get('college') or "Recognized College / Institution")
        student_dept = (profile.get('department') or data.get('department') or data.get('department_name') or internship['title'].replace(" Internship", "")) if profile else (data.get('department') or internship['title'].replace(" Internship", ""))
        student_degree = (profile.get('degree') or data.get('degree') or "Recognized Degree Program") if profile else "Recognized Degree Program"

        # ================================================
        # 4) MASTER RECORD (OPTIONAL)
        # ================================================
        try:
            from utils.master_record_service import save_master_record
            master_data = {
                "student_full_name": student_name or "Student Candidate",
                "student_email": to_email or "",
                "student_mobile": student_mobile or "",
                "college_name": student_college or "Recognized College / Institution",
                "degree": student_degree or "Recognized Degree Program",
                "department": student_dept or "Technology",
                "internship_position": f"{internship['title']} Intern",
                "internship_domain": internship['title'],
                "internship_start_date": start_date_str,
                "internship_end_date": end_date_str,
                "project_title": internship.get('project_name') or f"{internship['title']} Capstone Project",
                "mentor_name": internship.get('guide_name') or "Dr. A. K. Sharma",
                "mentor_designation": "Technical Director",
                "offer_id": offer_id,
                "certificate_id": cert_id,
                "user_id": user['sub'],
                "application_id": app_id
            }
            master_rec, master_errors = save_master_record(master_data)
            if master_errors:
                print(f"[Master Record Warning] {master_errors}")
                warnings.append(f"Record validation: {', '.join(master_errors[:2])}")
        except Exception as e:
            print(f"[Master Record Error] {e}")
            import traceback
            traceback.print_exc()
            warnings.append("Internal record creation skipped; your enrollment is still saved.")

        date_str = start_date_str

        # ================================================
        # 5) GENERATE OFFER LETTER PDF (OPTIONAL)
        # ================================================
        pdf_bytes = b""
        file_path = ""
        try:
            pdf_bytes = generate_offer_letter_pdf(
                student_name=student_name or "Student Candidate",
                internship_title=internship.get('title') or "Internship",
                date_str=date_str,
                save_id=app_id,
                company_name=internship.get('company_name') or "Web Intern Platform",
                start_date=start_date_str,
                end_date=end_date_str,
                duration=f"{duration_weeks} Weeks",
                location=internship.get('location') or "Virtual / Remote",
                skills_tools=internship.get('skills_tools'),
                tasks_projects=internship.get('tasks_projects'),
                offer_id=offer_id,
                college_name=student_college or "Institution",
                department=student_dept or "Department"
            )
            try:
                os.makedirs(Config.GENERATED_OFFERS_DIR, exist_ok=True)
                file_path = os.path.join(Config.GENERATED_OFFERS_DIR, f"offer_{app_id}.pdf")
                with open(file_path, 'wb') as f:
                    f.write(pdf_bytes)
                print(f"[Offer Letter Generated] App: {app_id}, File: {file_path}, Size: {len(pdf_bytes)} bytes")
            except Exception as save_err:
                print(f"[PDF Save Warning] Could not save PDF to disk: {save_err}")
                file_path = ""
                warnings.append("Offer letter file could not be cached; it will be re-generated when you download it.")
        except Exception as e:
            print(f"[PDF Generation Warning] Could not generate PDF: {e}")
            import traceback
            traceback.print_exc()
            pdf_bytes = b""
            file_path = ""
            warnings.append("Offer letter PDF could not be generated now; please download it from the dashboard later.")

        # ================================================
        # 6) DOCUMENT RECORD (OPTIONAL)
        # ================================================
        doc_id = str(uuid.uuid4())
        email_status = "QUEUED"
        msg_id = f"async_msg_{app_id[:8]}"
        try:
            execute_db("""
                INSERT INTO documents (id, application_id, student_id, document_type, document_number, file_path, status, email_status, email_message_id)
                VALUES (?, ?, ?, 'OFFER_LETTER', ?, ?, 'ISSUED', ?, ?)
            """, (doc_id, app_id, user['sub'], offer_id, file_path or "", email_status, msg_id))
        except Exception as e:
            print(f"[Documents Table INSERT Warning] {e}")
            doc_id = None
            warnings.append("Document tracking not saved; your enrollment is unaffected.")

        # ================================================
        # 7) SEND EMAIL (ASYNC BACKGROUND THREAD, OPTIONAL)
        # ================================================
        def _do_send_email():
            try:
                print(f"[Email Thread Start] Sending offer letter to {to_email}")
                if not to_email or '@' not in to_email:
                    print("[Email Skip] No valid email address.")
                    return
                success, result = send_offer_letter_email(
                    to_email=to_email,
                    student_name=student_name,
                    internship_title=internship['title'],
                    pdf_bytes=pdf_bytes if pdf_bytes else None,
                    start_date=start_date_str,
                    end_date=end_date_str,
                    duration=f"{duration_weeks} Weeks",
                    offer_id=offer_id
                )
                if not doc_id:
                    return
                if success:
                    print(f"[✅ Email Success] Updated document record with SENT status")
                    execute_db("""
                        UPDATE documents SET email_status = 'SENT', email_message_id = ?
                        WHERE id = ?
                    """, (str(result.get('id', msg_id)) if isinstance(result, dict) else msg_id, doc_id))
                else:
                    print(f"[❌ Email Failed] {result}")
                    execute_db("""
                        UPDATE documents SET email_status = 'FAILED', email_message_id = ?
                        WHERE id = ?
                    """, (str(result)[:200], doc_id))
            except Exception as ex:
                print(f"[❌ Async Email Exception]: {ex}")
                try:
                    if doc_id:
                        execute_db("""
                            UPDATE documents SET email_status = 'ERROR'
                            WHERE id = ?
                        """, (doc_id,))
                except:
                    pass

        try:
            email_thread = threading.Thread(target=_do_send_email, daemon=True)
            email_thread.start()
            print(f"[Email Thread] Started for application {app_id}")
        except Exception as e:
            print(f"[Email Thread Start Warning] {e}")
            warnings.append("Email service not available right now; download the offer letter from the dashboard.")

        # ================================================
        # 8) GOOGLE SHEETS SYNC (ALREADY ASYNC INSIDE, WRAP FOR SAFETY)
        # ================================================
        try:
            sync_offer_letter_to_google_sheets({
                "offer_id": offer_id,
                "student_id": user['sub'],
                "student_name": student_name,
                "email": to_email,
                "mobile": student_mobile,
                "college": student_college,
                "department": student_dept,
                "degree": student_degree,
                "course_name": internship['title'],
                "role": internship.get('role') or internship['title'],
                "company": internship.get('company_name') or "Web Intern Platform",
                "start_date": start_date_str,
                "end_date": end_date_str,
                "duration": f"{duration_weeks} Weeks",
                "location": internship.get('location') or "Virtual / Remote",
                "issue_date": date_str,
                "document_status": "ISSUED",
                "email_status": email_status,
                "email_message_id": msg_id
            }, document_id=doc_id)
        except Exception as e:
            print(f"[Google Sheets Sync Warning] {e}")
            warnings.append("Google Sheets sync skipped.")

        # ================================================
        # 9) FINAL VERIFICATION + RETURN (MUST ALWAYS HIT)
        # ================================================
        new_app = query_db("SELECT * FROM applications WHERE id = ?", (app_id,), one=True)
        if not new_app:
            print(f"[ERROR] Application not found after creation: {app_id}")
            return jsonify({'error': 'Application was not saved properly. Please try again.'}), 500

        print(f"[Application Verified] Enrollment saved successfully: {app_id}")
        message = 'Enrollment successful! Your internship has been saved to your account.'
        if file_path:
            message = 'Application & Enrollment submitted successfully! Your official offer letter has been generated and has been queued for email.'
        return jsonify({
            'message': message,
            'application': new_app,
            'enrollment': new_app,
            'offer_letter_id': offer_id,
            'warnings': warnings,
            'email_pending': bool(to_email),
            'offer_download_url': f'/api/applications/{app_id}/offer-letter.pdf'
        }), 201

    except Exception as top_err:
        print(f"[CREATE APPLICATION TOP-LEVEL EXCEPTION] {top_err}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Something went wrong during enrollment. Please refresh the page and try again. ({str(top_err)[:60]})'
        }), 500

@application_bp.route('/api/applications/me', methods=['GET'])
@application_bp.route('/applications/me', methods=['GET'])
@jwt_required
def get_my_applications():
    user = request.user
    user_email = user.get('email', '')

    # Auto-link orphaned records for this email
    relink_user_data_by_email(user['sub'], user_email)

    apps = query_db("""
        SELECT a.*, 
               COALESCE(i.title, a.internship_id) as internship_title, 
               COALESCE(i.slug, '') as internship_slug, 
               COALESCE(i.duration_weeks, 4) as duration_weeks, 
               COALESCE(i.cover_image_url, '') as cover_image_url,
               COALESCE(i.company_name, 'Web Intern Platform') as company_name,
               COALESCE(i.location, 'Virtual') as location,
               COALESCE(i.skills_tools, '') as skills_tools,
               COALESCE(i.tasks_projects, '') as tasks_projects,
               COALESCE(s.name, 'Unknown Sector') as sector_name, 
               c.id as certificate_id, 
               c.is_verified_paid,
               CASE WHEN c.is_verified_paid = 1 THEN 1 ELSE 0 END as paid
        FROM applications a
        LEFT JOIN internships i ON a.internship_id = i.id
        LEFT JOIN sectors s ON i.sector_id = s.id
        LEFT JOIN certificates c ON a.id = c.application_id
        WHERE a.user_id = ? OR a.user_id IN (SELECT id FROM profiles WHERE LOWER(email) = LOWER(?))
        ORDER BY a.applied_at DESC
    """, (user['sub'], user_email))

    for app_item in apps:
        # Calculate weekly progress
        approved_subs = query_db("""
            SELECT COUNT(*) as cnt FROM submissions
            WHERE application_id = ? AND status IN ('approved', 'graded')
        """, (app_item['id'],), one=True)
        
        completed_weeks = approved_subs['cnt'] if approved_subs else 0
        app_item['completed_weeks'] = completed_weeks
        app_item['progress_percent'] = int((completed_weeks / (app_item['duration_weeks'] or 4)) * 100) if app_item['duration_weeks'] else 0
        
        # Get ALL submissions for this application (not just latest)
        all_submissions = query_db("""
            SELECT * FROM submissions
            WHERE application_id = ?
            ORDER BY week_number ASC
        """, (app_item['id'],))
        app_item['submissions'] = all_submissions or []
        
        # Latest submission for quick ref
        latest_sub = query_db("""
            SELECT * FROM submissions
            WHERE application_id = ?
            ORDER BY week_number DESC LIMIT 1
        """, (app_item['id'],), one=True)
        app_item['latest_submission'] = latest_sub

    return jsonify({'applications': apps, 'enrollments': apps}), 200

@application_bp.route('/api/applications/<app_id>', methods=['GET'])
@application_bp.route('/applications/<app_id>', methods=['GET'])
@jwt_required
def get_application_detail(app_id):
    user = request.user
    user_email = user.get('email', '')

    app_record = query_db("""
        SELECT a.*, i.title as internship_title, i.slug as internship_slug, i.duration_weeks, i.full_description,
               s.name as sector_name, c.id as certificate_id, c.is_verified_paid
        FROM applications a
        JOIN internships i ON a.internship_id = i.id
        JOIN sectors s ON i.sector_id = s.id
        LEFT JOIN certificates c ON a.id = c.application_id
        WHERE a.id = ? AND (a.user_id = ? OR a.user_id IN (SELECT id FROM profiles WHERE LOWER(email) = LOWER(?)) OR ? = 'admin')
    """, (app_id, user['sub'], user_email, user.get('role')), one=True)

    if not app_record:
        return jsonify({'error': 'Application record not found.'}), 404

    tasks = query_db("SELECT * FROM internship_tasks WHERE internship_id = ? ORDER BY week_number ASC", (app_record['internship_id'],))
    submissions = query_db("SELECT * FROM submissions WHERE application_id = ? ORDER BY week_number ASC", (app_id,))

    sub_map = {s['week_number']: s for s in submissions}

    for task in tasks:
        task['submission'] = sub_map.get(task['week_number'])

    app_record['tasks'] = tasks
    return jsonify({'application': app_record, 'enrollment': app_record}), 200

@application_bp.route('/api/applications/<app_id>/offer-letter.pdf', methods=['GET'])
def download_offer_letter(app_id):
    print(f"[DEBUG] Offer Letter Request - App ID: {app_id}")
    
    # First try to serve from cache (no auth needed for cached files)
    file_path = os.path.join(Config.GENERATED_OFFERS_DIR, f"offer_{app_id}.pdf")
    print(f"[DEBUG] Cache Path: {file_path}, Exists: {os.path.exists(file_path)}")
    
    if os.path.exists(file_path):
        print(f"[Offer Letter Served from Cache] App: {app_id}")
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f'Offer_Letter_{app_id[:8]}.pdf'
        )

    # For non-cached, try to get user from JWT if available
    user = None
    try:
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        if user_id:
            user = {'sub': user_id}
    except:
        pass

    # Get application - allow access if file is cached OR if user is authenticated
    if user:
        print(f"[DEBUG] User authenticated: {user['sub']}")
        app_record = query_db("""
            SELECT a.*, i.title as internship_title, i.duration_weeks, i.company_name, i.location, i.skills_tools, i.tasks_projects
            FROM applications a
            JOIN internships i ON a.internship_id = i.id
            WHERE a.id = ? AND (a.user_id = ? OR 'admin' = ?)
        """, (app_id, user['sub'], user.get('role', 'user')), one=True)
    else:
        # For public access, still get the application (anyone with app_id can view)
        print(f"[DEBUG] Public access request")
        app_record = query_db("""
            SELECT a.*, i.title as internship_title, i.duration_weeks, i.company_name, i.location, i.skills_tools, i.tasks_projects
            FROM applications a
            JOIN internships i ON a.internship_id = i.id
            WHERE a.id = ?
        """, (app_id,), one=True)
    
    print(f"[DEBUG] Query result: {app_record is not None}")

    if not app_record:
        print(f"[ERROR] Application not found for ID: {app_id}")
        return jsonify({'error': 'Offer letter not found. Application does not exist.'}), 404

    # Regenerate if not cached
    print(f"[Offer Letter Not Cached] Regenerating for App: {app_id}")
    
    profile = query_db("SELECT * FROM profiles WHERE id = ?", (app_record['user_id'],), one=True)
    student_name = profile['full_name'] if profile else "Intern Candidate"
    date_str = app_record.get('start_date') or datetime.datetime.now().strftime("%B %d, %Y")

    try:
        pdf_bytes = generate_offer_letter_pdf(
            student_name=student_name,
            internship_title=app_record['internship_title'],
            date_str=date_str,
            save_id=app_id,
            company_name=app_record.get('company_name') or "Web Intern Platform",
            start_date=app_record.get('start_date'),
            end_date=app_record.get('end_date'),
            duration=f"{app_record.get('duration_weeks') or 4} Weeks",
            location=app_record.get('location') or "Virtual / Remote",
            skills_tools=app_record.get('skills_tools'),
            tasks_projects=app_record.get('tasks_projects'),
            offer_id=app_record.get('offer_letter_id')
        )
        
        # Cache for next time
        os.makedirs(Config.GENERATED_OFFERS_DIR, exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"[Offer Letter Generated and Cached] App: {app_id}, Size: {len(pdf_bytes)} bytes")
        
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'inline; filename="Offer_Letter_{app_id[:8]}.pdf"'}
        )
    except Exception as e:
        print(f"[Offer Letter PDF Generation Error] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate offer letter: {str(e)}'}), 500
