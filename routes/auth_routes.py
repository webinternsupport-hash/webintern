import json
import uuid
import datetime
import requests
import bcrypt
from flask import Blueprint, request, jsonify, make_response, render_template_string
from database import query_db, execute_db
from utils.auth import generate_jwt, check_password, jwt_required, relink_user_data_by_email
from utils.email_service import send_forgot_password_email, _dispatch_email
from utils.google_sheets_service import sync_user_registration_to_google_sheets, sync_user_login_to_google_sheets
from config import Config
from supabase import create_client

auth_bp = Blueprint('auth_bp', __name__)

DEFAULT_SUPABASE_URL = "https://fzmdeigwxiesegvtuafk.supabase.co"
DEFAULT_SUPABASE_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ6bWRlaWd3eGllc2VndnR1YWZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg0MjA2NDAsImV4cCI6MjEwMzk5NjY0MH0.aqk90jQu4yBCgc0wi9zA0cMHf5XZ31OPVc3hcED0_J8"
DEFAULT_SUPABASE_SERVICE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ6bWRlaWd3eGllc2VndnR1YWZrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4ODQyMDY0MCwiZXhwIjoyMTAzOTk2NjQwfQ.osKcbobbZPLz7RpO0zVgyHbIPJC2l6QDF6MBQ-W0uTA"

def get_supabase_admin():
    url = (Config.SUPABASE_URL or DEFAULT_SUPABASE_URL).strip()
    key = (Config.SUPABASE_SERVICE_ROLE_KEY or DEFAULT_SUPABASE_SERVICE).strip()
    return create_client(url, key)

def get_supabase_anon():
    url = (Config.SUPABASE_URL or DEFAULT_SUPABASE_URL).strip()
    key = (Config.SUPABASE_ANON_KEY or DEFAULT_SUPABASE_ANON).strip()
    return create_client(url, key)

@auth_bp.route('/api/auth/config', methods=['GET'])
@auth_bp.route('/auth/config', methods=['GET'])
def get_auth_config():
    """Return public Supabase configuration for frontend initialization."""
    return jsonify({
        'supabase_url': getattr(Config, 'SUPABASE_URL', None) or DEFAULT_SUPABASE_URL,
        'supabase_anon_key': getattr(Config, 'SUPABASE_ANON_KEY', None) or DEFAULT_SUPABASE_ANON,
        'google_client_id': getattr(Config, 'GOOGLE_CLIENT_ID', '') or ''
    }), 200

@auth_bp.route('/api/auth/complete-profile', methods=['POST'])
@auth_bp.route('/auth/complete-profile', methods=['POST'])
@jwt_required
def complete_profile():
    """Complete user profile with required fields after Google login."""
    user = request.user
    data = request.get_json() or {}
    
    full_name = data.get('full_name', '').strip() or user.get('name')
    phone = data.get('phone', '').strip()
    phone_country_code = data.get('phone_country_code', '+91').strip()
    college = data.get('college', '').strip() or data.get('college_name', '').strip()
    department = data.get('department', '').strip() or data.get('department_name', '').strip()
    degree = data.get('degree', '').strip()
    
    # Validation
    if not full_name:
        return jsonify({'error': 'Full name is required.'}), 400
    if not phone:
        return jsonify({'error': 'Phone number is required.'}), 400
    if not college:
        return jsonify({'error': 'College name is required.'}), 400
    if not department:
        return jsonify({'error': 'Department is required.'}), 400
    
    # Update in local DB
    try:
        existing = query_db("SELECT id FROM profiles WHERE id = ?", (user['sub'],), one=True)
        if existing:
            execute_db("""
                UPDATE profiles 
                SET full_name = ?, phone = ?, phone_country_code = ?, college = ?, department = ?, degree = ?
                WHERE id = ?
            """, (full_name, phone, phone_country_code, college, department, degree, user['sub']))
        else:
            execute_db("""
                INSERT INTO profiles (id, full_name, email, phone, phone_country_code, college, department, degree)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user['sub'], full_name, user.get('email'), phone, phone_country_code, college, department, degree))
    except Exception as e:
        print(f"[Profile Update Error]: {e}")
    
    # Update in Supabase if available
    try:
        supabase_admin = get_supabase_admin()
        update_data = {
            'name': full_name,
            'mobile': phone,
            'phone_country_code': phone_country_code,
            'college': college,
            'department': department,
            'degree': degree,
            'profile_complete': True
        }
        supabase_admin.table('profiles').update(update_data).eq('id', user['sub']).execute()
    except Exception as e:
        print(f"[Supabase Profile Update Warning]: {e}")
    
    return jsonify({
        'message': 'Profile completed successfully!',
        'user': {
            'id': user['sub'],
            'email': user.get('email'),
            'full_name': full_name,
            'phone': phone,
            'college': college,
            'department': department,
            'degree': degree,
            'profile_complete': True,
            'role': 'student'
        }
    }), 200

def sync_profile_to_local_db(user_id, full_name, email, phone="", phone_country_code="+91", marketing_opt_in=False):
    """Sync profile record to SQLite database for compatibility with existing routes."""
    try:
        existing = query_db("SELECT id FROM profiles WHERE id = ? OR email = ?", (user_id, email), one=True)
        if existing:
            execute_db(
                "UPDATE profiles SET full_name = ?, email = ?, phone = ?, phone_country_code = ?, marketing_opt_in = ? WHERE id = ?",
                (full_name, email, phone, phone_country_code, 1 if marketing_opt_in else 0, existing['id'])
            )
        else:
            execute_db(
                "INSERT INTO profiles (id, full_name, email, phone, phone_country_code, marketing_opt_in) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, full_name, email, phone, phone_country_code, 1 if marketing_opt_in else 0)
            )
    except Exception as e:
        print(f"[SQLite Sync Warning]: {e}")

def safe_upsert_profile(supabase_admin, profile_dict):
    """Helper to safely upsert profiles even if certain columns differ in Postgres schema."""
    try:
        supabase_admin.table('profiles').upsert(profile_dict).execute()
    except Exception as e:
        err_str = str(e)
        if 'email' in err_str and 'column' in err_str:
            fallback_dict = {k: v for k, v in profile_dict.items() if k != 'email'}
            supabase_admin.table('profiles').upsert(fallback_dict).execute()
        else:
            print(f"[Profiles Upsert Warning]: {e}")

@auth_bp.route('/api/auth/register', methods=['POST'])
@auth_bp.route('/auth/register', methods=['POST'])
@auth_bp.route('/api/auth/signup', methods=['POST'])
@auth_bp.route('/auth/signup', methods=['POST'])
def register_user():
    """Register user with local DB and Supabase Auth."""
    data = request.get_json() or {}
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip().lower()
    phone = data.get('phone', '').strip()
    phone_country_code = data.get('phone_country_code', '+91').strip()
    college = data.get('college', '').strip() or data.get('college_name', '').strip()
    department = data.get('department', '').strip() or data.get('department_name', '').strip()
    degree = data.get('degree', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    terms_accepted = data.get('terms_accepted', False)
    marketing_opt_in = data.get('marketing_opt_in', False)

    # Validations
    if not full_name:
        return jsonify({'error': 'Full name is required.'}), 400
    if not email:
        return jsonify({'error': 'Email address is required.'}), 400
    if not password:
        return jsonify({'error': 'Password is required.'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long.'}), 400
    if confirm_password and password != confirm_password:
        return jsonify({'error': 'Passwords do not match.'}), 400
    if not terms_accepted:
        return jsonify({'error': 'You must agree to the Terms & Conditions and Privacy Policy.'}), 400

    full_mobile = f"{phone_country_code} {phone}".strip() if phone else ""
    user_id = str(uuid.uuid4())
    hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print(f"[REGISTER DEBUG] Creating account for email: {email}")
    print(f"[REGISTER DEBUG] Password hash length: {len(hashed_pwd)}")
    print(f"[REGISTER DEBUG] Hash type: {type(hashed_pwd)}")

    try:
        # Check existing in SQLite
        existing = query_db("SELECT id FROM profiles WHERE email = ?", (email,), one=True)
        if existing:
            return jsonify({'error': 'An account with this email address already exists. Please sign in instead.'}), 400

        try:
            supabase_admin = get_supabase_admin()
            res = supabase_admin.auth.admin.create_user({
                'email': email,
                'password': password,
                'email_confirm': True,
                'user_metadata': {'name': full_name}
            })
            if res.user:
                user_id = str(res.user.id)
                safe_upsert_profile(supabase_admin, {
                    'id': user_id,
                    'name': full_name,
                    'email': email,
                    'mobile': full_mobile,
                    'phone_verified': True,
                    'auth_provider': 'email',
                    'terms_accepted': True,
                    'marketing_opt_in': marketing_opt_in,
                    'profile_complete': True
                })
        except Exception as se:
            print(f"[Supabase Admin Sync Warning]: {se}")

        execute_db(
            "INSERT INTO profiles (id, full_name, email, phone, phone_country_code, college, department, degree, password_hash, auth_provider, terms_accepted, marketing_opt_in) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'email', 1, ?)",
            (user_id, full_name, email, phone, phone_country_code, college, department, degree, hashed_pwd, 1 if marketing_opt_in else 0)
        )
        
        # CRITICAL VERIFICATION: Verify password hash was saved correctly
        saved_profile = query_db("SELECT password_hash FROM profiles WHERE id = ?", (user_id,), one=True)
        if saved_profile:
            print(f"[REGISTER VERIFY] ✅ Password hash saved successfully")
            print(f"[REGISTER VERIFY] Saved hash length: {len(saved_profile.get('password_hash', ''))}")
        else:
            print(f"[REGISTER ERROR] ❌ Failed to verify password hash save")

        relink_user_data_by_email(user_id, email)

        sync_user_registration_to_google_sheets({
            'id': user_id,
            'full_name': full_name,
            'email': email,
            'mobile': full_mobile,
            'college': college,
            'department': department,
            'auth_provider': 'email'
        })

        token = generate_jwt({
            'sub': user_id,
            'email': email,
            'name': full_name,
            'role': 'student'
        })

        resp = make_response(jsonify({
            'message': 'Account created successfully!',
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'full_name': full_name,
                'mobile': full_mobile,
                'college': college,
                'department': department,
                'degree': degree,
                'profile_complete': True,
                'role': 'student'
            }
        }))
        resp.set_cookie('access_token', token, httponly=True, samesite='Lax', max_age=86400)
        return resp, 200

    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 400

@auth_bp.route('/api/auth/login', methods=['POST'])
@auth_bp.route('/auth/login', methods=['POST'])
def login_user():
    """Login user with Email and Password using Local DB and Supabase Auth."""
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()  # CRITICAL: Normalize email to lowercase
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email address and password are required.'}), 400

    print(f"\n[LOGIN DEBUG] Email (normalized): {email}")
    print(f"[LOGIN DEBUG] Password length: {len(password)}")

    # 1. Check local SQLite DB first - with proper email normalization
    local_profile = query_db("SELECT * FROM profiles WHERE LOWER(email) = LOWER(?)", (email,), one=True)
    
    if local_profile:
        print(f"[LOGIN DEBUG] ✅ Profile found by email: {local_profile.get('id')}")
        print(f"[LOGIN DEBUG] Password hash exists: {bool(local_profile.get('password_hash'))}")
        
        if local_profile.get('password_hash'):
            # CRITICAL FIX: Only attempt bcrypt if password_hash exists
            try:
                pwd_hash = local_profile['password_hash']
                # Handle case where hash might be stored as string
                if isinstance(pwd_hash, str):
                    pwd_hash_bytes = pwd_hash.encode('utf-8')
                else:
                    pwd_hash_bytes = pwd_hash
                
                print(f"[LOGIN DEBUG] Password hash type: {type(pwd_hash)}, length: {len(str(pwd_hash))}")
                print(f"[LOGIN DEBUG] Attempting bcrypt.checkpw...")
                
                password_match = bcrypt.checkpw(password.encode('utf-8'), pwd_hash_bytes)
                print(f"[LOGIN DEBUG] Password match result: {password_match}")
                
                if password_match:
                    print(f"[LOGIN DEBUG] ✅ PASSWORD VERIFIED - Generating token...")
                    token = generate_jwt({
                        'sub': local_profile['id'],
                        'email': email,
                        'name': local_profile['full_name'],
                        'role': 'student'
                    })

                    relink_user_data_by_email(local_profile['id'], email)

                    sync_user_login_to_google_sheets({
                        'id': local_profile['id'],
                        'full_name': local_profile['full_name'],
                        'email': email,
                        'mobile': local_profile.get('phone') or local_profile.get('mobile') or '',
                        'college': local_profile.get('college', ''),
                        'auth_provider': 'email'
                    })

                    # CRITICAL FIX: Fetch user's enrolled internships at login
                    enrollments = query_db("""
                        SELECT a.*, 
                               COALESCE(i.title, a.internship_id) as internship_title, 
                               COALESCE(i.slug, '') as internship_slug, 
                               COALESCE(i.duration_weeks, 4) as duration_weeks, 
                               COALESCE(i.cover_image_url, '') as cover_image_url,
                               COALESCE(i.company_name, 'Web Intern Platform') as company_name,
                               COALESCE(i.location, 'Virtual') as location,
                               '💼' as internship_emoji,
                               COALESCE(s.name, 'Unknown Sector') as sector_name
                        FROM applications a
                        LEFT JOIN internships i ON a.internship_id = i.id
                        LEFT JOIN sectors s ON i.sector_id = s.id
                        WHERE a.user_id = ? OR a.user_id IN (SELECT id FROM profiles WHERE LOWER(email) = LOWER(?))
                        ORDER BY a.applied_at DESC
                        LIMIT 10
                    """, (local_profile['id'], email)) or []

                    resp = make_response(jsonify({
                        'message': 'Login successful.',
                        'token': token,
                        'user': {
                            'id': local_profile['id'],
                            'email': email,
                            'full_name': local_profile['full_name'],
                            'mobile': local_profile.get('phone') or local_profile.get('mobile') or '',
                            'college': local_profile.get('college', ''),
                            'profile_complete': True,
                            'role': 'student'
                        },
                        'enrollments': enrollments
                    }))
                    resp.set_cookie('access_token', token, httponly=True, samesite='Lax', max_age=86400)
                    print(f"[LOGIN SUCCESS] User {email} logged in successfully with {len(enrollments)} enrollments")
                    return resp, 200
                else:
                    print(f"[LOGIN DEBUG] ❌ PASSWORD MISMATCH - bcrypt.checkpw returned False")
                    return jsonify({'error': 'Invalid email or password.'}), 401
            except Exception as e:
                print(f"[LOGIN ERROR] Password verification exception: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': 'Invalid email or password.'}), 401
        else:
            print(f"[LOGIN DEBUG] ⚠️ No password_hash found for user - trying Supabase auth")
    else:
        print(f"[LOGIN DEBUG] ❌ No profile found for email: {email}")

    try:
        print(f"[LOGIN DEBUG] Attempting Supabase authentication for: {email}")
        supabase_anon = get_supabase_anon()
        supabase_admin = get_supabase_admin()

        # Sign in via Supabase Auth
        auth_res = supabase_anon.auth.sign_in_with_password({
            'email': email,
            'password': password
        })

        if not auth_res.user:
            print(f"[LOGIN DEBUG] ❌ Supabase auth failed - no user returned")
            return jsonify({'error': 'Invalid email or password.'}), 401

        print(f"[LOGIN DEBUG] ✅ Supabase auth successful, user_id: {auth_res.user.id}")
        user_id = str(auth_res.user.id)

        # Retrieve profile from Supabase profiles table by ID
        prof_res = supabase_admin.table('profiles').select('*').eq('id', user_id).execute()
        
        profile = None
        if prof_res.data and len(prof_res.data) > 0:
            profile = prof_res.data[0]
        else:
            default_profile = {
                'id': user_id,
                'name': auth_res.user.user_metadata.get('name', email.split('@')[0]),
                'email': email,
                'mobile': '',
                'phone_verified': True,
                'auth_provider': 'email',
                'terms_accepted': True,
                'marketing_opt_in': False,
                'profile_complete': True
            }
            safe_upsert_profile(supabase_admin, default_profile)
            profile = default_profile
            sync_profile_to_local_db(user_id, profile['name'], email)

        token = generate_jwt({
            'sub': user_id,
            'email': email,
            'name': profile.get('name') or email.split('@')[0],
            'role': 'student'
        })

        sync_user_login_to_google_sheets({
            'id': user_id,
            'full_name': profile.get('name') or email.split('@')[0],
            'email': email,
            'mobile': profile.get('mobile', ''),
            'college': profile.get('college', ''),
            'auth_provider': 'email'
        })

        # CRITICAL FIX: Fetch user's enrolled internships at login
        enrollments = query_db("""
            SELECT a.*, 
                   COALESCE(i.title, a.internship_id) as internship_title, 
                   COALESCE(i.slug, '') as internship_slug, 
                   COALESCE(i.duration_weeks, 4) as duration_weeks, 
                   COALESCE(i.cover_image_url, '') as cover_image_url,
                   COALESCE(i.company_name, 'Web Intern Platform') as company_name,
                   COALESCE(i.location, 'Virtual') as location,
                   '💼' as internship_emoji,
                   COALESCE(s.name, 'Unknown Sector') as sector_name
            FROM applications a
            LEFT JOIN internships i ON a.internship_id = i.id
            LEFT JOIN sectors s ON i.sector_id = s.id
            WHERE a.user_id = ? OR a.user_id IN (SELECT id FROM profiles WHERE LOWER(email) = LOWER(?))
            ORDER BY a.applied_at DESC
            LIMIT 10
        """, (user_id, email)) or []

        resp = make_response(jsonify({
            'message': 'Login successful.',
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'full_name': profile.get('name') or email.split('@')[0],
                'mobile': profile.get('mobile', ''),
                'college': profile.get('college', ''),
                'profile_complete': True,
                'role': 'student'
            },
            'enrollments': enrollments
        }))
        resp.set_cookie('access_token', token, httponly=True, samesite='Lax', max_age=86400)
        return resp, 200

    except Exception as e:
        err_msg = str(e)
        if 'invalid credentials' in err_msg.lower() or 'invalid login' in err_msg.lower() or 'invalid email' in err_msg.lower():
            return jsonify({'error': 'Invalid email address or password.'}), 401
        return jsonify({'error': f'Authentication failed: {err_msg}'}), 400

def google_sub_to_uuid(user_id):
    """Convert Google numeric/string ID to a deterministic UUID compatible with Supabase Postgres schema."""
    try:
        uuid.UUID(str(user_id))
        return str(user_id)
    except Exception:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"google:{user_id}"))

def get_or_create_supabase_auth_user(supabase_admin, email, name):
    """Ensure user exists in Supabase auth.users table to satisfy profiles foreign key constraint."""
    try:
        res = supabase_admin.auth.admin.create_user({
            'email': email,
            'email_confirm': True,
            'user_metadata': {'name': name}
        })
        if res.user:
            return str(res.user.id)
    except Exception as e:
        print(f"[Supabase Auth Admin Note]: {e}")

    try:
        users_list = supabase_admin.auth.admin.list_users()
        for u in users_list:
            if u.email and u.email.lower() == email.lower():
                return str(u.id)
    except Exception as e:
        print(f"[Supabase Auth Admin List Users Warning]: {e}")

    return google_sub_to_uuid(email)

@auth_bp.route('/oauth2callback')
@auth_bp.route('/api/auth/google/callback')
def google_oauth_callback():
    """Handle Google OAuth 2.0 redirect callback."""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error or not code:
        err_msg = error or "Authorization code missing."
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Authentication Error</title></head>
        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h2 style="color: #e53e3e;">Google Sign-In Failed</h2>
            <p>{err_msg}</p>
            <a href="/#/login" style="padding: 10px 20px; background: #0B3D91; color: white; border-radius: 5px; text-decoration: none;">Return to Sign In</a>
        </body>
        </html>
        """
        return render_template_string(html), 400

    try:
        token_url = "https://oauth2.googleapis.com/token"
        scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
        if 'localhost' not in request.host and '127.0.0.1' not in request.host:
            scheme = 'https'
        redirect_uri = f"{scheme}://{request.host}/oauth2callback"
        
        token_data = {
            'code': code,
            'client_id': Config.GOOGLE_CLIENT_ID,
            'client_secret': Config.GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        token_res = requests.post(token_url, data=token_data, timeout=15)
        token_json = token_res.json()
        
        access_token = token_json.get('access_token')
        if not access_token:
            raise Exception(token_json.get('error_description') or 'Failed to obtain access token from Google.')

        userinfo_res = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=15
        )
        userinfo = userinfo_res.json()
        
        raw_user_id = str(userinfo.get('id'))
        email = userinfo.get('email', '').strip().lower()
        name = userinfo.get('name', '').strip() or email.split('@')[0]

        if not raw_user_id or not email:
            raise Exception('Google profile did not return valid email address.')

        supabase_admin = get_supabase_admin()
        user_id = get_or_create_supabase_auth_user(supabase_admin, email, name)

        prof_res = supabase_admin.table('profiles').select('*').eq('id', user_id).execute()
        profile = prof_res.data[0] if (prof_res.data and len(prof_res.data) > 0) else None

        if not profile:
            profile = {
                'id': user_id,
                'name': name,
                'email': email,
                'mobile': '',
                'phone_verified': True,
                'auth_provider': 'google',
                'google_account_id': raw_user_id,
                'sync_enabled': True,
                'terms_accepted': True,
                'marketing_opt_in': False,
                'profile_complete': True
            }
            safe_upsert_profile(supabase_admin, profile)
            sync_profile_to_local_db(user_id, name, email)
            # Also sync to local DB with Google account ID
            from database import execute_db
            try:
                execute_db("""
                    UPDATE profiles SET google_account_id = ?, auth_provider = 'google', sync_enabled = 1 
                    WHERE id = ?
                """, (raw_user_id, user_id))
            except Exception as e:
                print(f"[Warning] Could not update google_account_id: {e}")
        else:
            # Update Google account ID if not already set
            if not profile.get('google_account_id'):
                profile['google_account_id'] = raw_user_id
                profile['auth_provider'] = 'google'
                profile['sync_enabled'] = True
                safe_upsert_profile(supabase_admin, profile)
                from database import execute_db
                try:
                    execute_db("""
                        UPDATE profiles SET google_account_id = ?, auth_provider = 'google', sync_enabled = 1 
                        WHERE id = ?
                    """, (raw_user_id, user_id))
                except Exception as e:
                    print(f"[Warning] Could not update google_account_id: {e}")

        app_token = generate_jwt({
            'sub': profile['id'],
            'email': email,
            'name': name,
            'role': 'student'
        })

        user_json = json.dumps({
            'id': profile['id'],
            'email': email,
            'full_name': name,
            'profile_complete': True,
            'auth_provider': 'google',
            'role': 'student'
        })
        token_json_str = json.dumps(app_token)

        callback_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Successful</title>
            <script>
                localStorage.setItem('access_token', {token_json_str});
                localStorage.setItem('user_profile', {user_json});
                window.location.href = '/#/dashboard';
            </script>
        </head>
        <body style="font-family: sans-serif; text-align: center; padding-top: 100px;">
            <h3 style="color: #0B3D91;">Google Authentication Successful!</h3>
            <p>Redirecting to your dashboard...</p>
        </body>
        </html>
        """
        resp = make_response(render_template_string(callback_html))
        resp.set_cookie('access_token', app_token, httponly=True, samesite='Lax', max_age=86400)
        return resp
    except Exception as e:
        err_msg = str(e)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>OAuth Callback Error</title></head>
        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h2 style="color: #e53e3e;">Authentication Error</h2>
            <p>{err_msg}</p>
            <a href="/#/login" style="padding: 10px 20px; background: #0B3D91; color: white; border-radius: 5px; text-decoration: none;">Return to Sign In</a>
        </body>
        </html>
        """
        return render_template_string(html), 400

@auth_bp.route('/api/auth/google-sync', methods=['POST'])
def sync_google_user():
    """Sync profile and handle provider linking for users logging in via Google OAuth."""
    data = request.get_json() or {}
    user_id = data.get('id')
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip()
    credential = data.get('credential')
    access_token = data.get('access_token')

    if credential and (not email or not user_id):
        try:
            res = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={credential}', timeout=10)
            if res.status_code == 200:
                tinfo = res.json()
                user_id = str(tinfo.get('sub'))
                email = tinfo.get('email', '').strip().lower()
                name = tinfo.get('name', name) or email.split('@')[0]
        except Exception as e:
            print(f"[Google TokenInfo Error]: {e}")

    if access_token and (not email or not user_id):
        try:
            res = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers={'Authorization': f'Bearer {access_token}'}, timeout=10)
            if res.status_code == 200:
                uinfo = res.json()
                user_id = str(uinfo.get('id'))
                email = uinfo.get('email', '').strip().lower()
                name = uinfo.get('name', name) or email.split('@')[0]
        except Exception as e:
            print(f"[Google UserInfo Error]: {e}")

    if not email:
        return jsonify({'error': 'Email is required for Google auth sync.'}), 400

    profile = None
    try:
        # ✅ FIX: Check if user already exists in local DB by EMAIL (not by Google ID)
        # This ensures the same user gets the same user_id across logins
        existing_local = query_db("SELECT * FROM profiles WHERE email = ?", (email,), one=True)
        
        if existing_local:
            # User exists - reuse their existing ID to preserve applications
            user_uuid = existing_local['id']
            profile = {
                'id': user_uuid,
                'name': existing_local['full_name'] or name or email.split('@')[0],
                'email': email,
                'mobile': existing_local.get('phone') or '',
                'phone_country_code': existing_local.get('phone_country_code', '+91'),
                'college': existing_local.get('college', ''),
                'department': existing_local.get('department', ''),
                'degree': existing_local.get('degree', ''),
                'auth_provider': existing_local.get('auth_provider', 'google')
            }
            # Update auth provider if was email-only
            if existing_local.get('auth_provider') == 'email':
                execute_db("UPDATE profiles SET auth_provider = ? WHERE id = ?", ('both', user_uuid))
                profile['auth_provider'] = 'both'
        else:
            # New user via Google
            try:
                supabase_admin = get_supabase_admin()
                user_uuid = get_or_create_supabase_auth_user(supabase_admin, email, name or email.split('@')[0])
                
                prof_res = supabase_admin.table('profiles').select('*').eq('id', user_uuid).execute()
                profile = prof_res.data[0] if (prof_res.data and len(prof_res.data) > 0) else None

                if not profile:
                    new_profile = {
                        'id': user_uuid,
                        'name': name or email.split('@')[0],
                        'email': email,
                        'mobile': '',
                        'phone_verified': True,
                        'auth_provider': 'google',
                        'terms_accepted': True,
                        'marketing_opt_in': False,
                        'profile_complete': False
                    }
                    safe_upsert_profile(supabase_admin, new_profile)
                    profile = new_profile
                    sync_profile_to_local_db(user_uuid, name or email.split('@')[0], email)
            except Exception as se:
                print(f"[Supabase Sync Note]: {se}")
                # Fallback: create deterministic UUID for new Google user
                user_uuid = google_sub_to_uuid(user_id or email)
                sync_profile_to_local_db(user_uuid, name or email.split('@')[0], email)
                profile = {
                    'id': user_uuid,
                    'name': name or email.split('@')[0],
                    'email': email,
                    'mobile': '',
                    'auth_provider': 'google'
                }

        token = generate_jwt({
            'sub': profile['id'],
            'email': email,
            'name': profile.get('name') or name or email.split('@')[0],
            'role': 'student'
        })

        profile_complete = bool(
            profile.get('name') and profile.get('email') and 
            profile.get('mobile') and 
            profile.get('college') and 
            profile.get('department')
        )

        resp = make_response(jsonify({
            'message': 'Google authentication successful.',
            'token': token,
            'user': {
                'id': profile['id'],
                'email': email,
                'full_name': profile.get('name') or name or email.split('@')[0],
                'mobile': profile.get('mobile', ''),
                'college': profile.get('college', ''),
                'department': profile.get('department', ''),
                'degree': profile.get('degree', ''),
                'phone_country_code': profile.get('phone_country_code', '+91'),
                'profile_complete': profile_complete,
                'auth_provider': profile.get('auth_provider', 'google'),
                'role': 'student'
            }
        }))
        resp.set_cookie('access_token', token, httponly=True, samesite='Lax', max_age=86400)
        return resp, 200

    except Exception as e:
        return jsonify({'error': f'Failed to sync Google user: {str(e)}'}), 400

@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Trigger password reset email flow using Resend integration."""
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'error': 'Email address is required.'}), 400

    try:
        user = query_db("SELECT id, full_name FROM profiles WHERE email = ?", (email,), one=True)
        if not user:
            # Return generic success to prevent email enumeration
            return jsonify({'message': 'If your email is registered, you will receive a password reset link shortly.'}), 200

        reset_code = str(uuid.uuid4().hex[:8]).upper()
        reset_id = str(uuid.uuid4())
        hashed_token = bcrypt.hashpw(reset_code.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        expires_at = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

        execute_db(
            "INSERT INTO password_resets (id, email, token_hash, expires_at, consumed) VALUES (?, ?, ?, ?, 0)",
            (reset_id, email, hashed_token, expires_at)
        )

        reset_link = f"{request.host_url}#/reset-password?email={email}&code={reset_code}"
        success, res = send_forgot_password_email(email, reset_link=reset_link, reset_code=reset_code)

        if success:
            return jsonify({
                'message': f'Password reset email sent to {email} successfully via Resend.'
            }), 200
        else:
            return jsonify({'error': f'Failed to send password reset email via Resend: {res}'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to process password reset email: {str(e)}'}), 400

@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password using secure token code."""
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    code = data.get('code', '').strip().upper()
    new_password = data.get('password', '') or data.get('new_password', '')

    if not email or not code or not new_password:
        return jsonify({'error': 'Email, verification code, and new password are required.'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long.'}), 400

    # Find valid unconsumed reset token
    records = query_db("""
        SELECT * FROM password_resets 
        WHERE email = ? AND consumed = 0 
        ORDER BY created_at DESC
    """, (email,))

    valid_record = None
    for r in records:
        if bcrypt.checkpw(code.encode('utf-8'), r['token_hash'].encode('utf-8')):
            valid_record = r
            break

    if not valid_record:
        return jsonify({'error': 'Invalid or expired password reset code.'}), 400

    # Check expiration
    exp_time = datetime.datetime.strptime(valid_record['expires_at'], "%Y-%m-%d %H:%M:%S")
    if datetime.datetime.now() > exp_time:
        return jsonify({'error': 'Password reset token has expired. Please request a new link.'}), 400

    # Hash new password & update
    hashed_pwd = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    execute_db("UPDATE profiles SET password_hash = ? WHERE email = ?", (hashed_pwd, email))
    execute_db("UPDATE password_resets SET consumed = 1 WHERE id = ?", (valid_record['id'],))

    return jsonify({'message': 'Password has been reset successfully. You can now log in.'}), 200

@auth_bp.route('/api/auth/test-email', methods=['POST'])
def test_email_endpoint():
    """Endpoint to trigger and test email sending via Resend API."""
    data = request.get_json() or {}
    to_email = data.get('to_email', 'delivered@resend.dev').strip().lower()
    subject = data.get('subject', 'Test Email from Web Intern')
    content = data.get('content', 'This is a test email sent via Resend API key integration.')

    html_content = f"""
    <div style="font-family: 'Inter', Arial, sans-serif; padding: 24px; border: 1px solid #DCE6F5; border-radius: 12px; max-width: 500px; margin: 0 auto;">
        <h2 style="color: #0B3D91; margin-top: 0;">web<span style="color: #2E7DFF;">intern</span></h2>
        <h3 style="color: #082B66;">{subject}</h3>
        <p style="color: #4B5563; line-height: 1.6;">{content}</p>
        <hr style="border: none; border-top: 1px solid #DCE6F5; margin: 20px 0;" />
        <p style="color: #9CA3AF; font-size: 12px; text-align: center;">Verified Resend Integration Test • Web Intern</p>
    </div>
    """
    
    success, result = _dispatch_email(to_email, subject, html_content)
    if success:
        return jsonify({'message': f'Email sent successfully to {to_email}', 'result': result}), 200
    else:
        return jsonify({'error': f'Email sending failed: {result}'}), 500

@auth_bp.route('/api/auth/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    admin = query_db("SELECT * FROM admins WHERE email = ?", (email,), one=True)
    if not admin or not check_password(password, admin['password_hash']):
        return jsonify({'error': 'Invalid administrator credentials.'}), 401

    token = generate_jwt({
        'sub': admin['id'],
        'email': admin['email'],
        'name': admin['full_name'],
        'role': 'admin'
    })

    resp = make_response(jsonify({
        'message': 'Admin authentication successful.',
        'token': token,
        'user': {
            'id': admin['id'],
            'email': admin['email'],
            'full_name': admin['full_name'],
            'role': 'admin'
        }
    }))
    resp.set_cookie('access_token', token, httponly=True, samesite='Lax', max_age=86400)
    return resp, 200

@auth_bp.route('/api/auth/me', methods=['GET'])
@jwt_required
def get_current_user():
    user_payload = request.user
    if user_payload.get('role') == 'admin':
        admin = query_db("SELECT id, email, full_name, created_at FROM admins WHERE id = ?", (user_payload['sub'],), one=True)
        if admin:
            admin['role'] = 'admin'
            return jsonify({'user': admin}), 200
    else:
        try:
            supabase_admin = get_supabase_admin()
            prof_res = supabase_admin.table('profiles').select('*').eq('id', user_payload['sub']).execute()
            if prof_res.data and len(prof_res.data) > 0:
                p = prof_res.data[0]
                profile_complete = bool(
                    p.get('name') and p.get('email') and 
                    p.get('mobile') and p.get('college') and 
                    p.get('department')
                )
                return jsonify({
                    'user': {
                        'id': p['id'],
                        'full_name': p.get('name') or user_payload.get('name'),
                        'email': user_payload.get('email'),
                        'mobile': p.get('mobile'),
                        'college': p.get('college'),
                        'department': p.get('department'),
                        'degree': p.get('degree'),
                        'phone_country_code': p.get('phone_country_code', '+91'),
                        'profile_complete': profile_complete,
                        'auth_provider': p.get('auth_provider', 'email'),
                        'role': 'student'
                    }
                }), 200
        except Exception as e:
            print(f"[Supabase Profile Fetch Error]: {e}")

        profile = query_db("""
            SELECT id, full_name, email, phone, phone_country_code, college, department, degree, avatar_url, created_at 
            FROM profiles WHERE id = ?
        """, (user_payload['sub'],), one=True)
        if profile:
            profile_complete = bool(
                profile.get('full_name') and profile.get('email') and 
                profile.get('phone') and profile.get('college') and 
                profile.get('department')
            )
            profile['profile_complete'] = profile_complete
            profile['role'] = 'student'
            return jsonify({'user': profile}), 200

    return jsonify({'error': 'User not found.'}), 404
