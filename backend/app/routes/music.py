from flask import Blueprint, jsonify, request, send_file
from sqlalchemy import func, desc, case, not_, and_, or_
from ..models.music import Music
from ..models.user_preference import UserPreference
from ..models.user import User
from .. import db
import os
import sys
from ..controllers.music_controller import MusicController
from ..utils.decorators import token_required

music_bp = Blueprint('music', __name__)
music_controller = MusicController()


MUSICAL_KEYS_UA = {
    0: 'До',      # C
    1: 'До#',     # C#
    2: 'Ре',      # D
    3: 'Ре#',     # D#
    4: 'Мі',      # E
    5: 'Фа',      # F
    6: 'Фа#',     # F#
    7: 'Соль',    # G
    8: 'Соль#',   # G#
    9: 'Ля',      # A
    10: 'Ля#',    # A#
    11: 'Сі'      # B
}

def get_token_from_header():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None

def get_current_user_id():
    """Get current user ID from token"""
    token = get_token_from_header()
    if not token:
        return None
    
    payload = User.verify_token(token)
    if not payload:
        return None
        
    return payload['user_id']

def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'message': 'Token is missing or invalid'}), 401
        return f(*args, **kwargs)
    return decorated

def check_minimum_preferences(f):
    """Decorator to check if user has minimum required preferences (5)"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'message': 'Token is missing or invalid'}), 401
        
        from ..models.user_preference import UserPreference
        preference_count = UserPreference.query.filter_by(user_id=user_id).count()
        
        if preference_count < 5:
            return jsonify({
                'error': 'Insufficient preferences',
                'needs_cold_start': True,
                'preference_count': preference_count,
                'minimum_required': 5,
                'message': 'You need at least 5 favorite songs to use this feature. Please complete the setup process.'
            }), 400
        
        return f(*args, **kwargs)
    return decorated

def format_musical_key_ua(key, mode):
    """Format musical key in Ukrainian"""
    if key is None or mode is None:
        return None
    
    key_name = MUSICAL_KEYS_UA.get(key, 'Невідомо')
    mode_name = 'мажор' if mode == 1 else 'мінор'
    
    return f"{key_name} {mode_name}"

@music_bp.route('/random', methods=['GET'])
def get_random_songs():
    """Get random songs, prioritizing songs that have MP3 files available"""
    return music_controller.get_random_songs()

@music_bp.route('/file/<song_id>', methods=['GET'])
def get_song_file(song_id):
    """Serve the MP3 file for a song"""
    return music_controller.get_song_file(song_id)

@music_bp.route('/tags', methods=['GET'])
def get_tags():
    """Get list of all tags with their song counts, prioritizing tags with playable songs"""
    return music_controller.get_tags()

@music_bp.route('/songs/<song_id>', methods=['GET'])
def get_song_details(song_id):
    """Get detailed information about a specific song"""
    return music_controller.get_song_details(song_id)

@music_bp.route('/search', methods=['GET'])
def search_songs():
    """Search songs by name, artist, or tag"""
    return music_controller.search_music()

@music_bp.route('/daily-mix', methods=['GET'])
@token_required
def get_daily_mix():
    """Get daily mix playlist based on user's most recent preference or specified seed"""
    return music_controller.get_daily_mix()

@music_bp.route('/ai-status', methods=['GET'])
def get_ai_status():
    """Get the status of the AI recommender model"""
    return music_controller.get_ai_status()

@music_bp.route('/ai-reload', methods=['POST'])
@token_required
def reload_ai_model():
    """Reload the AI recommender model (admin function)"""
    return music_controller.reload_ai_model()

@music_bp.route('/by-genre', methods=['GET'])
def get_songs_by_genre():
    """Get songs by genre"""
    genre = request.args.get('genre', '').strip()
    return music_controller.get_music_by_genre(genre)

@music_bp.route('/genre-recommendations-from-favorites', methods=['GET'])
@token_required
def get_genre_recommendations_from_favorites():
    """Get recommendations based on user's favorites with the same genre"""
    return music_controller.get_genre_recommendations_from_favorites()