from typing import Dict, Any, Optional, Tuple
from flask import jsonify, request
from marshmallow import Schema, ValidationError
from ..utils.helpers import standardize_response, validate_required_fields

class BaseController:
    """Base controller class with common functionality"""
    
    def __init__(self):
        pass
    
    def validate_json_data(self, schema: Schema, data: Dict[str, Any] = None) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple]]:
        """Validate JSON data using marshmallow schema"""
        if data is None:
            data = request.get_json()
        
        if not data:
            return None, (jsonify(standardize_response(
                message="No JSON data provided", 
                status="error"
            )), 400)
        
        try:
            validated_data = schema.load(data)
            return validated_data, None
        except ValidationError as err:
            return None, (jsonify(standardize_response(
                message="Validation error", 
                data=err.messages,
                status="error"
            )), 400)
    
    def success_response(self, data: Any = None, message: str = None, status_code: int = 200):
        """Create standardized success response"""
        return jsonify(standardize_response(data=data, message=message)), status_code
    
    def error_response(self, message: str, status_code: int = 400, data: Any = None):
        """Create standardized error response"""
        return jsonify(standardize_response(
            message=message, 
            data=data, 
            status="error"
        )), status_code
    
    def handle_exception(self, e: Exception, default_message: str = "An error occurred"):
        """Handle exceptions and return appropriate error response"""
        if isinstance(e, ValueError):
            return self.error_response(str(e), 400)
        else:
            print(f"Unexpected error: {e}")
            return self.error_response(default_message, 500) 