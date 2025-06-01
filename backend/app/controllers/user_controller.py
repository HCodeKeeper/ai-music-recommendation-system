from typing import Tuple
from flask import request
from ..services.user_service import UserService
from ..schemas.user_schema import UserCreateSchema, UserLoginSchema, UserSchema
from ..utils.decorators import get_token_from_header
from ..models.user import User
from .base_controller import BaseController

class UserController(BaseController):
    """Controller for user-related operations"""
    
    def __init__(self):
        super().__init__()
        self.user_service = UserService()
        self.user_schema = UserSchema()
        self.user_create_schema = UserCreateSchema()
        self.user_login_schema = UserLoginSchema()
    
    def register(self) -> Tuple:
        """Register a new user"""
        try:
            validated_data, error_response = self.validate_json_data(self.user_create_schema)
            if error_response:
                return error_response
            
            user = self.user_service.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                name=validated_data['name']
            )
            
            token = user.generate_token()
            user_data = self.user_schema.dump(user)
            
            return self.success_response(
                data={'user': user_data, 'token': token},
                message="User registered successfully",
                status_code=201
            )
            
        except Exception as e:
            return self.handle_exception(e, "Error creating user")
    
    def login(self) -> Tuple:
        """Authenticate user login"""
        try:
            validated_data, error_response = self.validate_json_data(self.user_login_schema)
            if error_response:
                return error_response
            
            user = self.user_service.authenticate_user(
                email=validated_data['email'],
                password=validated_data['password']
            )
            
            if not user:
                return self.error_response("Invalid email or password", 401)
            
            token = user.generate_token()
            user_data = self.user_schema.dump(user)
            
            return self.success_response(
                data={'user': user_data, 'token': token},
                message="Login successful"
            )
            
        except Exception as e:
            return self.handle_exception(e, "Error during login")
    
    def verify_token(self) -> Tuple:
        """Verify JWT token and return user data"""
        try:
            token = get_token_from_header()
            if not token:
                return self.error_response("Token is missing", 401)
            
            payload = User.verify_token(token)
            if not payload:
                return self.error_response("Token is invalid or expired", 401)
            
            user = self.user_service.get_by_id(payload['user_id'])
            if not user:
                return self.error_response("User not found", 404)
            
            user_data = self.user_schema.dump(user)
            return self.success_response(data={'user': user_data})
            
        except Exception as e:
            return self.handle_exception(e, "Error verifying token")
    
    def get_current_user(self) -> Tuple:
        """Get current user from token"""
        try:
            token = get_token_from_header()
            if not token:
                return self.error_response("Token is missing", 401)
            
            payload = User.verify_token(token)
            if not payload:
                return self.error_response("Token is invalid or expired", 401)
            
            user = self.user_service.get_by_id(payload['user_id'])
            if not user:
                return self.error_response("User not found", 404)
            
            return user, None
            
        except Exception as e:
            return None, self.handle_exception(e, "Error getting current user") 