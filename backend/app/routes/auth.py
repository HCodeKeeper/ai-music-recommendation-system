from flask import Blueprint
from ..controllers.user_controller import UserController
from ..utils.decorators import token_required

auth_bp = Blueprint('auth', __name__)
user_controller = UserController()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    return user_controller.register()

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user login"""
    return user_controller.login()

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token():
    """Verify JWT token and return user data"""
    return user_controller.verify_token() 