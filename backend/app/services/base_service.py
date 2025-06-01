from typing import Type, List, Optional, Dict, Any
from flask_sqlalchemy import SQLAlchemy
from .. import db

class BaseService:
    """Base service class with common database operations"""
    
    def __init__(self, model: Type[db.Model]):
        self.model = model
        self.db = db
    
    def get_by_id(self, id: Any) -> Optional[db.Model]:
        """Get a record by ID"""
        return self.model.query.get(id)
    
    def get_all(self, **filters) -> List[db.Model]:
        """Get all records with optional filters"""
        query = self.model.query
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.all()
    
    def create(self, data: Dict[str, Any]) -> db.Model:
        """Create a new record"""
        instance = self.model(**data)
        self.db.session.add(instance)
        self.db.session.commit()
        return instance
    
    def update(self, instance: db.Model, data: Dict[str, Any]) -> db.Model:
        """Update an existing record"""
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        self.db.session.commit()
        return instance
    
    def delete(self, instance: db.Model) -> bool:
        """Delete a record"""
        try:
            self.db.session.delete(instance)
            self.db.session.commit()
            return True
        except Exception:
            self.db.session.rollback()
            return False
    
    def paginate(self, page: int = 1, per_page: int = 20, **filters):
        """Paginate records with optional filters"""
        query = self.model.query
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.paginate(page=page, per_page=per_page, error_out=False) 