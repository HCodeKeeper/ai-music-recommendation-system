from flask import Blueprint
from ..controllers.preference_controller import PreferenceController
from ..utils.decorators import token_required

preferences_bp = Blueprint('preferences', __name__)
preference_controller = PreferenceController()

@preferences_bp.route('/check-cold-start', methods=['GET'])
@token_required
def check_cold_start():
    """Check if user needs cold start (either no preferences or < 5 preferences)"""
    return preference_controller.check_cold_start()

@preferences_bp.route('/add-preferences', methods=['POST'])
@token_required
def add_preferences():
    """Add multiple song preferences for a user (for cold start)"""
    return preference_controller.add_preferences()

@preferences_bp.route('/get-preferences', methods=['GET'])
@token_required
def get_preferences():
    """Get all preferences for the current user"""
    return preference_controller.get_preferences()

@preferences_bp.route('/add-preference', methods=['POST'])
@token_required
def add_preference():
    """Add a single song preference"""
    return preference_controller.add_preference()

@preferences_bp.route('/remove-preference', methods=['DELETE'])
@token_required
def remove_preference():
    """Remove a song preference"""
    return preference_controller.remove_preference()

@preferences_bp.route('/favourites-playlist', methods=['GET'])
@token_required
def get_favourites_playlist():
    """Get user's favourites playlist containing all songs from user_preferences"""
    return preference_controller.get_favourites_playlist() 