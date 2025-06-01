from functools import wraps
from flask import request, jsonify
from ..models.user import User

def get_token_from_header():
    """Extract token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
            
        payload = User.verify_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
            
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
            
        payload = User.verify_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
            
        user = User.query.get(payload['user_id'])
        if not user or not getattr(user, 'is_admin', False):
            return jsonify({'message': 'Admin privileges required'}), 403
            
        return f(*args, **kwargs)
    return decorated 