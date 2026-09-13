"""Sync user data to Supabase for persistence."""
import os
import json
from datetime import datetime
import uuid

# Try to import Supabase client
try:
    from supabase import create_client
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY) if SUPABASE_URL and SUPABASE_ANON_KEY else None
except Exception as e:
    print(f"[Supabase Init Warning] {e}")
    supabase = None


def sync_enrollment_to_supabase(user_id, enrollment_data):
    """Save enrollment (application) to Supabase."""
    if not supabase:
        print("[Supabase] Not initialized, skipping sync")
        return None
        
    try:
        # Map to your actual table/column names
        response = supabase.table('applications').insert({
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'internship_id': enrollment_data.get('internship_id'),
            'status': enrollment_data.get('status', 'active'),
            'start_date': enrollment_data.get('start_date'),
            'end_date': enrollment_data.get('end_date'),
            'offer_letter_id': enrollment_data.get('offer_letter_id'),
            'certificate_id': enrollment_data.get('certificate_id'),
            'applied_at': datetime.now().isoformat()
        }).execute()
        
        app_id = response.data[0]['id'] if response.data else None
        print(f"[Supabase Sync] Enrollment saved: {app_id}")
        return app_id
    except Exception as e:
        print(f"[Supabase Error] Failed to sync enrollment: {e}")
        return None


def sync_payment_to_supabase(user_id, application_id, payment_data):
    """Save payment to Supabase."""
    if not supabase:
        print("[Supabase] Not initialized, skipping sync")
        return None
        
    try:
        response = supabase.table('payments').insert({
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'application_id': application_id,
            'razorpay_order_id': payment_data.get('razorpay_order_id'),
            'razorpay_payment_id': payment_data.get('razorpay_payment_id'),
            'razorpay_signature': payment_data.get('razorpay_signature'),
            'amount_inr': payment_data.get('amount_inr', 199),
            'status': payment_data.get('status', 'created'),
            'created_at': datetime.now().isoformat()
        }).execute()
        
        payment_id = response.data[0]['id'] if response.data else None
        print(f"[Supabase Sync] Payment saved: {payment_id}")
        return payment_id
    except Exception as e:
        print(f"[Supabase Error] Failed to sync payment: {e}")
        return None


def sync_certificate_to_supabase(user_id, application_id, certificate_data):
    """Save certificate to Supabase."""
    if not supabase:
        print("[Supabase] Not initialized, skipping sync")
        return None
        
    try:
        response = supabase.table('certificates').insert({
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'application_id': application_id,
            'certificate_url': certificate_data.get('certificate_url'),
            'certificate_number': certificate_data.get('certificate_number'),
            'is_verified_paid': certificate_data.get('is_verified', True),
            'issued_at': certificate_data.get('issued_at', datetime.now().isoformat())
        }).execute()
        
        cert_id = response.data[0]['id'] if response.data else None
        print(f"[Supabase Sync] Certificate saved: {cert_id}")
        return cert_id
    except Exception as e:
        print(f"[Supabase Error] Failed to sync certificate: {e}")
        return None


def get_user_applications_from_supabase(user_id):
    """Fetch user's applications from Supabase."""
    if not supabase:
        return []
        
    try:
        response = supabase.table('applications').select('*').eq('user_id', user_id).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"[Supabase Error] Failed to get applications: {e}")
        return []


def get_user_payments_from_supabase(user_id):
    """Fetch user's payments from Supabase."""
    if not supabase:
        return []
        
    try:
        response = supabase.table('payments').select('*').eq('user_id', user_id).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"[Supabase Error] Failed to get payments: {e}")
        return []


def get_user_certificates_from_supabase(user_id):
    """Fetch user's certificates from Supabase."""
    if not supabase:
        return []
        
    try:
        response = supabase.table('certificates').select('*').eq('user_id', user_id).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"[Supabase Error] Failed to get certificates: {e}")
        return []
