from .token_utils import generate_token
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from flask import current_app, jsonify
import pytz

def generate_auth_token(user, keep_session):
    token = generate_token(user['_id'],user['role'], keep_session, user["active"])
    if keep_session:
        expiration_time = datetime.now(pytz.timezone('Europe/Paris')) + timedelta(days=14)
    else:
        expiration_time = datetime.now(pytz.timezone('Europe/Paris')) + timedelta(hours=8)
    return token, expiration_time

def set_auth_cookie(response, token, expiration_time, current_app):
    expiration_timestamp = int(expiration_time.timestamp())
    same_site = "Strict" if current_app.config['PRODUCTION'] else "None"
    response.set_cookie('authToken', token, expires=expiration_timestamp, httponly=True, samesite=same_site, secure=True)
