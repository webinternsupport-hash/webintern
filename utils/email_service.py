import base64
import requests
from config import Config

def _get_resend_key():
    return (Config.RESEND_API_KEY or "").strip()

def _dispatch_email(to_email, subject, html_content, attachments=None):
    print(f"\n{'='*60}")
    print(f"[_dispatch_email] STARTING EMAIL SEND")
    print(f"[_dispatch_email] To: {to_email}")
    print(f"[_dispatch_email] Subject: {subject}")
    print(f"[_dispatch_email] Attachments: {len(attachments) if attachments else 0}")
    
    api_key = _get_resend_key()
    from_email = getattr(Config, 'RESEND_FROM_EMAIL', 'notifications@webintern.in') or 'notifications@webintern.in'
    
    print(f"[_dispatch_email] API Key configured: {bool(api_key)}")
    print(f"[_dispatch_email] From email: {from_email}")
    
    # CRITICAL FIX: Check if API key is properly configured
    if not api_key or api_key.startswith("re_demo") or api_key in ["", "your_resend_api_key"]:
        print(f"[❌ EMAIL BLOCKED] RESEND API KEY NOT CONFIGURED!")
        print(f"[❌ EMAIL BLOCKED] Email will NOT be sent to {to_email}")
        print(f"[❌ EMAIL BLOCKED] Configure RESEND_API_KEY in .env file to enable real email sending")
        print(f"{'='*60}\n")
        return False, {"error": "Email service not configured", "status": "not_configured"}
    
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key[:10]}...",  # Log only first 10 chars for security
        "Content-Type": "application/json"
    }
    
    payload = {
        "from": f"Web Intern <{from_email}>",
        "to": [to_email] if isinstance(to_email, str) else to_email,
        "subject": subject,
        "html": html_content[:100] + "..." if len(html_content) > 100 else html_content
    }
    
    if attachments:
        payload["attachments"] = f"[{len(attachments)} file(s)]"
        
    print(f"[_dispatch_email] Payload preview: {payload}")
    
    try:
        print(f"[_dispatch_email] POSTing to {url}")
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        res = requests.post(url, headers=headers, json={
            "from": f"Web Intern <{from_email}>",
            "to": [to_email] if isinstance(to_email, str) else to_email,
            "subject": subject,
            "html": html_content,
            "attachments": attachments
        }, timeout=10, verify=False)
        
        print(f"[_dispatch_email] HTTP Status: {res.status_code}")
        
        if res.status_code in [200, 201]:
            data = res.json()
            print(f"[✅ EMAIL SENT] To: {to_email}, ID: {data.get('id')}")
            print(f"{'='*60}\n")
            return True, data
        else:
            err_body = res.text
            print(f"[❌ EMAIL FAILED] HTTP {res.status_code}: {err_body}")
            print(f"{'='*60}\n")
            return False, f"Email service error ({res.status_code}): {err_body}"
    except Exception as e:
        print(f"[❌ EMAIL EXCEPTION] {type(e).__name__}: {e}")
        print(f"{'='*60}\n")
        return False, {"error": str(e), "status": "failed"}

def send_forgot_password_email(to_email, reset_link=None, reset_code=None):
    subject = "Web Intern - Password Reset Request"
    if not reset_link:
        reset_link = "https://webintern.in/#/reset-password"
    
    code_html = f"""
        <div style="text-align: center; margin: 24px 0;">
            <span style="font-size: 28px; font-weight: 700; letter-spacing: 4px; color: #0B3D91; background: #EAF1FB; padding: 12px 24px; border-radius: 8px; display: inline-block;">
                {reset_code}
            </span>
        </div>
    """ if reset_code else ""

    html_content = f"""
    <div style="font-family: 'Inter', Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 24px; border: 1px solid #DCE6F5; border-radius: 12px; background-color: #FFFFFF;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #0B3D91; margin: 0; font-size: 24px;">web<span style="color: #2E7DFF;">intern</span></h2>
            <p style="color: #4B5563; font-size: 14px; margin-top: 4px;">Virtual Internship Platform</p>
        </div>
        <hr style="border: none; border-top: 1px solid #DCE6F5; margin: 20px 0;" />
        <h3 style="color: #082B66; font-size: 18px; margin-bottom: 12px;">Password Reset Request</h3>
        <p style="color: #4B5563; line-height: 1.5;">We received a request to reset your password for your Web Intern account.</p>
        {code_html}
        <div style="text-align: center; margin: 24px 0;">
            <a href="{reset_link}" style="background-color: #0B3D91; color: #FFFFFF; text-decoration: none; padding: 12px 28px; border-radius: 24px; font-weight: 600; display: inline-block;">Reset Password →</a>
        </div>
        <p style="color: #4B5563; font-size: 13px;">If you did not request a password reset, you can safely ignore this email.</p>
        <hr style="border: none; border-top: 1px solid #DCE6F5; margin: 20px 0;" />
        <p style="color: #9CA3AF; font-size: 12px; text-align: center;">© 2026 Web Intern. Secure Automated Verification System.</p>
    </div>
    """
    return _dispatch_email(to_email, subject, html_content)

def send_offer_letter_email(to_email, student_name, internship_title, pdf_bytes=None, start_date=None, end_date=None, duration="4 Weeks", offer_id=None):
    print(f"[Offer Letter Email] Starting email dispatch to {to_email}")
    subject = "Your WebIntern Internship Offer Letter"
    eff_start = start_date or "Immediate"
    eff_end = end_date or "4 Weeks from Start Date"
    eff_offer_id = offer_id or "WI-OFFER-2026"

    html_content = f"""
    <div style="font-family: 'Inter', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #DCE6F5; border-radius: 12px; background-color: #FFFFFF;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #0B3D91; margin: 0; font-size: 26px;">web<span style="color: #2E7DFF;">intern</span></h2>
        </div>
        <p style="color: #4B5563;">Dear <strong>{student_name}</strong>,</p>
        <p style="color: #4B5563; font-weight: 600;">Congratulations!</p>
        <p style="color: #4B5563; line-height: 1.6;">Your internship enrollment with WebIntern has been confirmed.</p>
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; margin: 16px 0; color: #334155;">
            <p style="margin: 4px 0;"><strong>Internship:</strong> {internship_title}</p>
            <p style="margin: 4px 0;"><strong>Start Date:</strong> {eff_start}</p>
            <p style="margin: 4px 0;"><strong>End Date:</strong> {eff_end}</p>
            <p style="margin: 4px 0;"><strong>Duration:</strong> {duration}</p>
            <p style="margin: 4px 0;"><strong>Offer ID:</strong> {eff_offer_id}</p>
        </div>
        <p style="color: #4B5563;">Your Offer Letter is attached to this email. You can also view it from your WebIntern dashboard.</p>
        <div style="text-align: center; margin: 24px 0;">
            <a href="https://webintern.in/#/dashboard" style="background-color: #0B3D91; color: #FFFFFF; text-decoration: none; padding: 12px 28px; border-radius: 24px; font-weight: 600; display: inline-block;">Go to Dashboard →</a>
        </div>
        <p style="color: #64748B; font-size: 13px;">Regards,<br/>WebIntern Team</p>
    </div>
    """
    
    attachments = None
    if pdf_bytes:
        print(f"[Offer Letter Email] PDF attached, size: {len(pdf_bytes)} bytes")
        clean_offer_id = str(eff_offer_id).replace('/', '_')
        encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        attachments = [{
            "filename": f"WebIntern_Offer_Letter_{clean_offer_id}.pdf",
            "content": encoded_pdf
        }]
    else:
        print(f"[⚠️ Offer Letter Email] No PDF provided - email will be sent without attachment")

    print(f"[Offer Letter Email] Calling _dispatch_email to {to_email}")
    result = _dispatch_email(to_email, subject, html_content, attachments=attachments)
    print(f"[Offer Letter Email] Result: {result}")
    return result

def send_certificate_email(to_email, student_name, internship_title, cert_id, pdf_bytes=None, start_date=None, end_date=None, verification_url=None):
    subject = "Your WebIntern Internship Completion Certificate"
    eff_start = start_date or "N/A"
    eff_end = end_date or "N/A"
    eff_verify_url = verification_url or f"https://webintern.in/verify/{cert_id}"

    html_content = f"""
    <div style="font-family: 'Inter', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #DCE6F5; border-radius: 12px; background-color: #FFFFFF;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #0B3D91; margin: 0; font-size: 26px;">web<span style="color: #2E7DFF;">intern</span></h2>
        </div>
        <p style="color: #4B5563;">Dear <strong>{student_name}</strong>,</p>
        <p style="color: #4B5563; font-weight: 600;">Congratulations on successfully completing your internship with WebIntern.</p>
        <p style="color: #4B5563; line-height: 1.6;">Your Internship Completion Certificate has been issued.</p>
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; margin: 16px 0; color: #334155;">
            <p style="margin: 4px 0;"><strong>Certificate ID:</strong> {cert_id}</p>
            <p style="margin: 4px 0;"><strong>Internship:</strong> {internship_title}</p>
            <p style="margin: 4px 0;"><strong>Start Date:</strong> {eff_start}</p>
            <p style="margin: 4px 0;"><strong>End Date:</strong> {eff_end}</p>
        </div>
        <p style="color: #4B5563;">Your certificate is attached to this email. You can also access it from your WebIntern dashboard.</p>
        <p style="color: #4B5563;"><strong>Certificate Verification:</strong> <a href="{eff_verify_url}" style="color: #2E7DFF;">{eff_verify_url}</a></p>
        <div style="text-align: center; margin: 24px 0;">
            <a href="{eff_verify_url}" style="background-color: #0B3D91; color: #FFFFFF; text-decoration: none; padding: 12px 28px; border-radius: 24px; font-weight: 600; display: inline-block;">Verify Certificate →</a>
        </div>
        <p style="color: #64748B; font-size: 13px;">Regards,<br/>WebIntern Team</p>
    </div>
    """

    attachments = None
    if pdf_bytes:
        encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        attachments = [{
            "filename": f"WebIntern_Certificate_{cert_id}.pdf",
            "content": encoded_pdf
        }]

    return _dispatch_email(to_email, subject, html_content, attachments=attachments)

def send_feedback_email(to_email, student_name, week_number, status, feedback_text):
    status_color = "#10B981" if status in ["approved", "graded"] else "#F59E0B"
    subject = f"Task Week {week_number} Evaluation Update - Web Intern"
    html_content = f"""
    <div style="font-family: 'Inter', Arial, sans-serif; max-width: 550px; margin: 0 auto; padding: 24px; border: 1px solid #DCE6F5; border-radius: 12px; background-color: #FFFFFF;">
        <h3 style="color: #082B66;">Task Evaluation Result</h3>
        <p style="color: #4B5563;">Hello <strong>{student_name}</strong>,</p>
        <p style="color: #4B5563;">Your submission for <strong>Week {week_number}</strong> has been reviewed:</p>
        <div style="padding: 16px; border-radius: 8px; background: #F8F9FA; border-left: 4px solid {status_color}; margin: 16px 0;">
            <p style="margin: 0; font-weight: 600; color: {status_color}; text-transform: uppercase; font-size: 13px;">Status: {status}</p>
            <p style="margin: 8px 0 0 0; color: #4B5563;">{feedback_text}</p>
        </div>
        <p style="color: #4B5563;">Log in to your student workspace to view complete details or proceed to the next module.</p>
    </div>
    """
    return _dispatch_email(to_email, subject, html_content)

def send_welcome_newsletter(to_email):
    subject = "Welcome to Web Intern Newsletter!"
    html_content = """
    <div style="font-family: 'Inter', Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 24px;">
        <h2 style="color: #0B3D91;">web<span style="color: #2E7DFF;">intern</span></h2>
        <h3>Thank you for subscribing!</h3>
        <p style="color: #4B5563;">You will now receive weekly career tips, newly launched virtual internships, and industry insights straight to your inbox.</p>
    </div>
    """
    return _dispatch_email(to_email, subject, html_content)

def send_contact_form_notification(sender_name, sender_email, sender_phone="", subject_line="", message_text=""):
    """
    Send incoming contact form submission directly to webinternsupport@gmail.com
    and send confirmation receipt to user.
    """
    support_email = "webinternsupport@gmail.com"
    eff_subject = f"[WebIntern Inquiry] {subject_line or 'New User Message'}: {sender_name}"
    eff_phone = sender_phone or "Not Provided"

    admin_html = f"""
    <div style="font-family: 'Inter', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #DCE6F5; border-radius: 12px; background-color: #FFFFFF;">
        <div style="background: linear-gradient(135deg, #082B66 0%, #0B3D91 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
            <h2 style="margin: 0; font-size: 22px; color: white;">WebIntern Support Inquiry Received</h2>
            <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 13px;">New user requirements message submitted via website contact form</p>
        </div>
        <div style="padding: 20px; border: 1px solid #E2E8F0; border-top: none; border-radius: 0 0 8px 8px; background-color: #F8FAFC;">
            <p style="margin: 6px 0; color: #1F2937;"><strong>Sender Name:</strong> {sender_name}</p>
            <p style="margin: 6px 0; color: #1F2937;"><strong>Sender Email:</strong> <a href="mailto:{sender_email}" style="color: #0B3D91; font-weight: 600;">{sender_email}</a></p>
            <p style="margin: 6px 0; color: #1F2937;"><strong>Phone Number:</strong> {eff_phone}</p>
            <p style="margin: 6px 0; color: #1F2937;"><strong>Subject:</strong> {subject_line or 'General Support Inquiry'}</p>
            <hr style="border: none; border-top: 1px solid #CBD5E1; margin: 16px 0;" />
            <p style="margin: 0 0 8px 0; font-weight: 700; color: #082B66;">Message & Requirement Details:</p>
            <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 6px; padding: 16px; font-size: 14px; line-height: 1.6; color: #1E293B; white-space: pre-wrap;">
{message_text}
            </div>
            <div style="margin-top: 24px; text-align: center;">
                <a href="mailto:{sender_email}?subject=Re: {subject_line or 'WebIntern Support Inquiry'}" style="background-color: #0B3D91; color: #FFFFFF; text-decoration: none; padding: 12px 28px; border-radius: 24px; font-weight: 600; display: inline-block;">Reply Direct to Sender ({sender_email}) →</a>
            </div>
        </div>
    </div>
    """

    admin_success, admin_res = _dispatch_email(support_email, eff_subject, admin_html)

    user_subject = "We received your message - WebIntern Support"
    user_html = f"""
    <div style="font-family: 'Inter', Arial, sans-serif; max-width: 550px; margin: 0 auto; padding: 24px; border: 1px solid #DCE6F5; border-radius: 12px; background-color: #FFFFFF;">
        <div style="text-align: center; margin-bottom: 16px;">
            <h2 style="color: #0B3D91; margin: 0; font-size: 26px;">web<span style="color: #2E7DFF;">intern</span></h2>
            <p style="color: #4B5563; font-size: 14px; margin-top: 2px;">Official Virtual Internship Platform</p>
        </div>
        <hr style="border: none; border-top: 1px solid #DCE6F5; margin: 16px 0;" />
        <p style="color: #1F2937;">Hello <strong>{sender_name}</strong>,</p>
        <p style="color: #4B5563; line-height: 1.6;">Thank you for contacting <strong>WebIntern Support</strong>. We have received your message and requirement details.</p>
        <p style="color: #4B5563; line-height: 1.6;">Our support team (<code>webinternsupport@gmail.com</code>) will review your message and get back to you shortly.</p>
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; margin: 16px 0; color: #334155; font-size: 13px;">
            <p style="margin: 2px 0; font-weight: 700;">Summary of Your Message:</p>
            <p style="margin: 6px 0; color: #4B5563;"><em>"{message_text[:200]}..."</em></p>
        </div>
        <p style="color: #64748B; font-size: 13px;">Best regards,<br/><strong>WebIntern Support Team</strong><br/><a href="mailto:webinternsupport@gmail.com" style="color: #0B3D91;">webinternsupport@gmail.com</a></p>
    </div>
    """
    _dispatch_email(sender_email, user_subject, user_html)

    return admin_success, admin_res

