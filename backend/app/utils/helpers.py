from typing import Dict, List, Any, Optional
from flask import jsonify

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Optional[str]:
    """Validate that all required fields are present in the data"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        return f"Missing required fields: {', '.join(missing_fields)}"
    return None

def standardize_response(data: Any = None, message: str = None, status: str = "success") -> Dict[str, Any]:
    """Standardize API response format"""
    response = {"status": status}
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return response

def paginate_query(query, page: int, per_page: int):
    """Helper to paginate database queries"""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    ) 