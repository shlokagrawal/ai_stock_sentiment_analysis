from flask import request, jsonify, current_app
from functools import wraps
from app.models.user import User
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def generate_token(user_id):
    """Generate JWT token for authentication"""
    
    expiration = datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
    
    payload = {
        'user_id': user_id,
        'exp': expiration
    }
    
    token = jwt.encode(
        payload,
        os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
        algorithm='HS256'
    )
    
    return token

def token_required(f):
    """Decorator to protect routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Verify token
            payload = jwt.decode(
                token,
                os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
                algorithms=['HS256']
            )
            
            # Get user from token
            current_user = User.query.get(payload['user_id'])
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
                
            if not current_user.is_active:
                return jsonify({'error': 'User account is inactive'}), 403
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to restrict routes to admin users only"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

def analyst_required(f):
    """Decorator to restrict routes to analyst or admin users"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role not in ['analyst', 'admin']:
            return jsonify({'error': 'Analyst privileges required'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated 