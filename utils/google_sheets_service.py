import os
import requests
import json
import threading
import datetime
from config import Config
from database import execute_db

def extract_clean_phone(obj):
    """Extract clean formatted phone/mobile number from dict or DB Row object."""
    if not obj:
        return ""
    
    mobile = ""
    code = ""
    
    if isinstance(obj, dict):
        mobile = obj.get('mobile') or obj.get('phone') or obj.get('student_mobile') or obj.get('student_phone') or ""
        code = obj.get('phone_country_code') or obj.get('country_code') or ""
    else:
        # SQLite Row or class instance
        try:
            mobile = obj['phone'] if 'phone' in obj.keys() else (obj['mobile'] if 'mobile' in obj.keys() else "")
        except Exception:
            mobile = getattr(obj, 'mobile', None) or getattr(obj, 'phone', None) or ""
            
        try:
            code = obj['phone_country_code'] if 'phone_country_code' in obj.keys() else ""
        except Exception:
            code = getattr(obj, 'phone_country_code', None) or ""

    mobile_str = str(mobile).strip() if mobile else ""
    code_str = str(code).strip() if code else ""

    if mobile_str and code_str and not mobile_str.startswith("+"):
        return f"{code_str} {mobile_str}".strip()
    return mobile_str

def _send_webhook_request(webhook_url, payload):
    """Post payload to Google Apps Script webhook with fallback redirect query support."""
    headers = {"Content-Type": "application/json"}
    try:
        res = requests.post(webhook_url, json=payload, headers=headers, timeout=10, allow_redirects=True)
        if res.status_code == 200:
            return True, "SUCCESS"
        else:
            # Fallback query parameter post if 302/redirect returned GET
            res_fb = requests.get(webhook_url, params={"payload": json.dumps(payload)}, timeout=10)
            if res_fb.status_code == 200:
                return True, "SUCCESS_GET_FALLBACK"
            return False, f"HTTP {res.status_code}: {res.text[:150]}"
    except Exception as e:
        return False, str(e)

def sync_offer_letter_to_google_sheets(offer_payload, document_id=None):
    """Asynchronously sync Offer Letter record to Google Sheets webhook without blocking user workflow."""
    def _do_sync():
        webhook_url = getattr(Config, 'GOOGLE_SHEETS_WEBHOOK_URL', '') or os.getenv("GOOGLE_SHEETS_WEBHOOK_URL", "")
        if not webhook_url:
            print("[Google Sheets Sync Note]: GOOGLE_SHEETS_WEBHOOK_URL not configured. Skipping remote sync.")
            return

        payload = {
            "type": "OFFER_LETTER",
            "offerId": offer_payload.get("offer_id"),
            "studentId": offer_payload.get("student_id"),
            "studentName": offer_payload.get("student_name"),
            "email": offer_payload.get("email"),
            "mobile": extract_clean_phone(offer_payload),
            "collegeName": offer_payload.get("college") or offer_payload.get("college_name", ""),
            "department": offer_payload.get("department", ""),
            "degree": offer_payload.get("degree", ""),
            "course": offer_payload.get("course_name"),
            "internshipRole": offer_payload.get("role"),
            "company": offer_payload.get("company", "Web Intern Platform"),
            "startDate": offer_payload.get("start_date"),
            "endDate": offer_payload.get("end_date"),
            "duration": offer_payload.get("duration", "4 Weeks"),
            "location": offer_payload.get("location", "Virtual / Remote"),
            "mentorName": offer_payload.get("mentor_name") or offer_payload.get("guide_name") or "Dr. A. K. Sharma",
            "issueDate": offer_payload.get("issue_date"),
            "documentStatus": offer_payload.get("document_status", "ISSUED"),
            "emailStatus": offer_payload.get("email_status", "SENT"),
            "emailMessageId": offer_payload.get("email_message_id", "")
        }

        success, err_msg = _send_webhook_request(webhook_url, payload)
        if success:
            print(f"[Google Sheets Sync Success]: Offer Letter {offer_payload.get('offer_id')}")
            if document_id:
                execute_db("UPDATE documents SET sheets_synced = 1, sheets_error = NULL WHERE id = ?", (document_id,))
        else:
            print(f"[Google Sheets Sync Warning]: {err_msg}")
            if document_id:
                execute_db("UPDATE documents SET sheets_synced = 0, sheets_error = ? WHERE id = ?", (err_msg, document_id))

    threading.Thread(target=_do_sync, daemon=True).start()

def sync_user_registration_to_google_sheets(user_payload):
    """Asynchronously sync Student Registration to Google Sheets webhook."""
    def _do_sync():
        webhook_url = getattr(Config, 'GOOGLE_SHEETS_WEBHOOK_URL', '') or os.getenv("GOOGLE_SHEETS_WEBHOOK_URL", "")
        if not webhook_url:
            print("[Google Sheets Sync Note]: GOOGLE_SHEETS_WEBHOOK_URL not configured. Skipping remote sync.")
            return

        payload = {
            "type": "USER_REGISTRATION",
            "studentId": user_payload.get("id"),
            "studentName": user_payload.get("full_name") or user_payload.get("name"),
            "email": user_payload.get("email"),
            "mobile": extract_clean_phone(user_payload),
            "collegeName": user_payload.get("college") or user_payload.get("college_name", ""),
            "department": user_payload.get("department", ""),
            "degree": user_payload.get("degree", ""),
            "authProvider": user_payload.get("auth_provider", "email"),
            "timestamp": datetime.datetime.now().isoformat()
        }

        success, err_msg = _send_webhook_request(webhook_url, payload)
        if success:
            print(f"[Google Sheets Sync Success]: Registration for {user_payload.get('email')}")
        else:
            print(f"[Google Sheets Sync Warning]: {err_msg}")

    threading.Thread(target=_do_sync, daemon=True).start()

def sync_user_login_to_google_sheets(user_payload):
    """Asynchronously sync Student Login activity to Google Sheets webhook."""
    def _do_sync():
        webhook_url = getattr(Config, 'GOOGLE_SHEETS_WEBHOOK_URL', '') or os.getenv("GOOGLE_SHEETS_WEBHOOK_URL", "")
        if not webhook_url:
            print("[Google Sheets Sync Note]: GOOGLE_SHEETS_WEBHOOK_URL not configured. Skipping remote sync.")
            return

        payload = {
            "type": "USER_LOGIN",
            "studentId": user_payload.get("id"),
            "studentName": user_payload.get("full_name") or user_payload.get("name"),
            "email": user_payload.get("email"),
            "mobile": extract_clean_phone(user_payload),
            "collegeName": user_payload.get("college") or user_payload.get("college_name", ""),
            "department": user_payload.get("department", ""),
            "degree": user_payload.get("degree", ""),
            "authProvider": user_payload.get("auth_provider", "email"),
            "timestamp": datetime.datetime.now().isoformat()
        }

        success, err_msg = _send_webhook_request(webhook_url, payload)
        if success:
            print(f"[Google Sheets Sync Success]: Login for {user_payload.get('email')}")
        else:
            print(f"[Google Sheets Sync Warning]: {err_msg}")

    threading.Thread(target=_do_sync, daemon=True).start()

def sync_certificate_to_google_sheets(cert_payload, document_id=None):
    """Asynchronously sync Certificate record to Google Sheets webhook without blocking user workflow."""
    def _do_sync():
        webhook_url = getattr(Config, 'GOOGLE_SHEETS_WEBHOOK_URL', '') or os.getenv("GOOGLE_SHEETS_WEBHOOK_URL", "")
        if not webhook_url:
            print("[Google Sheets Sync Note]: GOOGLE_SHEETS_WEBHOOK_URL not configured. Skipping remote sync.")
            return

        payload = {
            "type": "CERTIFICATE",
            "certificateId": cert_payload.get("certificate_id"),
            "studentId": cert_payload.get("student_id"),
            "studentName": cert_payload.get("student_name"),
            "email": cert_payload.get("email"),
            "mobile": extract_clean_phone(cert_payload),
            "collegeName": cert_payload.get("college") or cert_payload.get("college_name", ""),
            "department": cert_payload.get("department", ""),
            "degree": cert_payload.get("degree", ""),
            "course": cert_payload.get("course_name"),
            "internshipRole": cert_payload.get("role"),
            "company": cert_payload.get("company", "Web Intern Platform"),
            "startDate": cert_payload.get("start_date"),
            "endDate": cert_payload.get("end_date"),
            "duration": cert_payload.get("duration", "4 Weeks"),
            "guideName": cert_payload.get("guide_name") or cert_payload.get("mentor_name") or "Dr. A. K. Sharma",
            "projectName": cert_payload.get("project_name", "Enterprise Capstone"),
            "certificateDate": cert_payload.get("issue_date"),
            "issueDate": cert_payload.get("issue_date"),
            "documentStatus": cert_payload.get("document_status", "ISSUED"),
            "emailStatus": cert_payload.get("email_status", "SENT"),
            "emailMessageId": cert_payload.get("email_message_id", ""),
            "verificationUrl": cert_payload.get("verification_url", "")
        }

        success, err_msg = _send_webhook_request(webhook_url, payload)
        if success:
            print(f"[Google Sheets Sync Success]: Certificate {cert_payload.get('certificate_id')}")
            if document_id:
                execute_db("UPDATE documents SET sheets_synced = 1, sheets_error = NULL WHERE id = ?", (document_id,))
        else:
            print(f"[Google Sheets Sync Warning]: {err_msg}")
            if document_id:
                execute_db("UPDATE documents SET sheets_synced = 0, sheets_error = ? WHERE id = ?", (err_msg, document_id))

    threading.Thread(target=_do_sync, daemon=True).start()

def check_google_sheets_connection():
    """
    Check if Google Sheets Webhook is properly configured and reachable.
    Returns a dict with connection status, message, and configuration details.
    """
    webhook_url = getattr(Config, 'GOOGLE_SHEETS_WEBHOOK_URL', '') or os.getenv("GOOGLE_SHEETS_WEBHOOK_URL", "")
    
    if not webhook_url:
        return {
            "status": "misconfigured",
            "connected": False,
            "message": "GOOGLE_SHEETS_WEBHOOK_URL is not set in environment or config.",
            "webhook_url": None
        }

    try:
        res = requests.get(webhook_url, timeout=5, allow_redirects=True)
        if res.status_code == 200:
            try:
                data = res.json()
            except Exception:
                data = {"raw": res.text[:200]}
            return {
                "status": "connected",
                "connected": True,
                "message": "Google Sheets Webhook connection active and verified.",
                "webhook_url": webhook_url[:40] + "...",
                "response": data
            }
        else:
            return {
                "status": "error",
                "connected": False,
                "message": f"HTTP {res.status_code} from Google Sheets Webhook endpoint.",
                "webhook_url": webhook_url[:40] + "..."
            }
    except Exception as e:
        return {
            "status": "disconnected",
            "connected": False,
            "message": f"Failed to connect to Google Sheets Webhook: {str(e)}",
            "webhook_url": webhook_url[:40] + "..." if webhook_url else None
        }

