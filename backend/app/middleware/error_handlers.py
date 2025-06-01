from flask import jsonify
from marshmallow import ValidationError
from ..utils.helpers import standardize_response

def register_error_handlers(app):
    """Register global error handlers for the Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(standardize_response(
            message="Bad request",
            status="error"
        )), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify(standardize_response(
            message="Unauthorized",
            status="error"
        )), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify(standardize_response(
            message="Forbidden",
            status="error"
        )), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify(standardize_response(
            message="Resource not found",
            status="error"
        )), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify(standardize_response(
            message="Method not allowed",
            status="error"
        )), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify(standardize_response(
            message="Internal server error",
            status="error"
        )), 500
    
    @app.errorhandler(ValidationError)
    def validation_error(error):
        return jsonify(standardize_response(
            message="Validation error",
            data=error.messages,
            status="error"
        )), 400 