import os
import jwt
import datetime
import bcrypt
from functools import wraps
from flask import request, jsonify
from config import Config

DEFAULT_JWT_SECRET = "webintern_jwt_secret_key_2026_secure_token_982347"

def get_jwt_secret():
    secret = (getattr(Config, 'SECRET_KEY', None) or os.getenv("JWT_SECRET") or DEFAULT_JWT_SECRET).strip()
    return secret if secret else DEFAULT_JWT_SECRET

def generate_jwt(payload_data, expires_in_hours=24):
    secret = get_jwt_secret()
    payload = payload_data.copy()
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(hours=expires_in_hours)
    payload['iat'] = datetime.datetime.utcnow()
    token = jwt.encode(payload, secret, algorithm=Config.JWT_ALGORITHM)
    return token

def decode_jwt(token):
    secret = get_jwt_secret()
    try:
        payload = jwt.decode(token, secret, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            token = request.cookies.get('access_token')

        if not token:
            return jsonify({'error': 'Authentication token missing', 'code': 'UNAUTHORIZED'}), 401

        payload = decode_jwt(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token', 'code': 'INVALID_TOKEN'}), 401

        request.user = payload
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            token = request.cookies.get('access_token')

        if not token:
            return jsonify({'error': 'Admin token missing', 'code': 'UNAUTHORIZED'}), 401

        payload = decode_jwt(token)
        if not payload or payload.get('role') != 'admin':
            return jsonify({'error': 'Admin access required', 'code': 'FORBIDDEN'}), 403

        request.user = payload
        return f(*args, **kwargs)
    return decorated

def relink_user_data_by_email(user_id, email):
    """
    Ensure all applications, documents, master records, and payments belonging to an email
    are linked to the active profile's user_id so data is preserved across sessions and logins.
    """
    if not user_id or not email:
        return
    
    from database import execute_db
    try:
        # Update applications where user profile email matches but user_id differs
        execute_db("""
            UPDATE applications 
            SET user_id = ? 
            WHERE (user_id != ? OR user_id IS NULL) 
              AND (user_id IN (SELECT id FROM profiles WHERE LOWER(email) = LOWER(?)) 
                   OR id IN (SELECT application_id FROM master_internships WHERE LOWER(student_email) = LOWER(?)))
        """, (user_id, user_id, email, email))

        # Update documents
        execute_db("""
            UPDATE documents 
            SET student_id = ? 
            WHERE (student_id != ? OR student_id IS NULL) 
              AND student_id IN (SELECT id FROM profiles WHERE LOWER(email) = LOWER(?))
        """, (user_id, user_id, email))

        # Update master_internships
        execute_db("""
            UPDATE master_internships 
            SET user_id = ? 
            WHERE (user_id IS NULL OR user_id != ?) AND LOWER(student_email) = LOWER(?)
        """, (user_id, user_id, email))

        # Update payments
        execute_db("""
            UPDATE payments 
            SET user_id = ? 
            WHERE (user_id IS NULL OR user_id != ?) AND user_id IN (SELECT id FROM profiles WHERE LOWER(email) = LOWER(?))
        """, (user_id, user_id, email))
    except Exception as e:
        print(f"[Relink User Data Warning]: {e}")

