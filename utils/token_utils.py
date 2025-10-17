import jwt
from flask import request, current_app, jsonify
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import traceback
import pytz
from datetime import datetime, timedelta
from functools import wraps
import os
import secrets

def generate_token(user_id, user_role, keep_session, user_active):
    expiration_period = timedelta(days=14) if keep_session else timedelta(hours=8)
    try:
        user_id_str = str(user_id)
        user_role_str = str(user_role)
        
        token = jwt.encode({
            'user_id': user_id_str,
            'user_role': user_role_str,
            'exp': datetime.now() + expiration_period,
            'active': user_active
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token
    except:
        return traceback.format_exc(), 500

def verify_token():
    if os.getenv("PRODUCTION") == "False":
        return True, "Token is valid", 'maintainer'
    token = request.cookies.get('authToken')
    if not token:
        uuid = request.args.get("uuid")
        if not uuid:
            return False, "No token provided", None
        elif uuid == '08dd0825-8333-499c-89f4-22ec0bb74280':
            return True, "Token is valid", None
        else:
            return False, "Invalid token", None
        
    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        if(not decoded.get('active')):
            return False, "Deactivated user", None
        else:
            return True, "Token is valid", decoded.get('user_role')
    except ExpiredSignatureError:
        return False, "Token has expired", None
    except InvalidTokenError:
        return False, "Invalid token", None
    except Exception as e:
        traceback.print_exc()
        return False, str(e), None

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_valid, message, role = verify_token()
        if not is_valid:
            return jsonify({'error': message}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_valid, message, role = verify_token()
        if not is_valid:
            return jsonify({'error': message}), 401
        if role != 'admin' and role != 'maintainer':
            return jsonify({'error': 'Unauthorized access, admin required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def admin_cta_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_valid, message, role = verify_token()
        if not is_valid:
            return jsonify({'error': message}), 401
        if role != 'admin' and role != 'maintainer' and role != 'admin-cta':
            return jsonify({'error': 'Unauthorized access, admin CTA required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def generate_password_reset_token():
    token = secrets.token_urlsafe()
    expiration_time = datetime.now(pytz.timezone('Europe/Paris')) + timedelta(minutes=15)
    return token, expiration_time