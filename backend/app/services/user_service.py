from typing import Optional, Dict, Any
from ..models.user import User
from .base_service import BaseService

class UserService(BaseService):
    """Service for user-related business logic"""
    
    def __init__(self):
        super().__init__(User)
    
    def create_user(self, email: str, password: str, name: str) -> User:
        """Create a new user with hashed password"""
        if self.get_by_email(email):
            raise ValueError("Email already registered")
        
        user_data = {
            'email': email,
            'password': password,
            'name': name
        }
        
        user = User(**user_data)
        self.db.session.add(user)
        self.db.session.commit()
        return user
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_by_email(email)
        if user and user.check_password(password):
            return user
        return None
    
    def update_user(self, user: User, data: Dict[str, Any]) -> User:
        """Update user with validation"""
        if 'email' in data and data['email'] != user.email:
            if self.get_by_email(data['email']):
                raise ValueError("Email already exists")
        
        if 'password' in data:
            user.password = user._hash_password(data['password'])
            data.pop('password')
        
        return super().update(user, data)
    
    def get_user_preferences(self, user_id: int):
        """Get user's music preferences"""
        from ..models.user_preference import UserPreference
        return UserPreference.query.filter_by(user_id=user_id).all()
    
    def to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return user.to_dict() 