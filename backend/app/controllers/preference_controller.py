from typing import Tuple
from flask import request
from ..services.preference_service import PreferenceService
from ..schemas.preference_schema import PreferenceSchema, PreferenceCreateSchema
from ..utils.decorators import get_token_from_header
from ..models.user import User
from ..models.music import Music
from ..models.user_preference import UserPreference
from .. import db
from .base_controller import BaseController

class PreferenceController(BaseController):
    """Controller for user preference operations"""
    
    def __init__(self):
        super().__init__()
        self.preference_service = PreferenceService()
        self.preference_schema = PreferenceSchema()
        self.preference_create_schema = PreferenceCreateSchema()
    
    def get_current_user_id(self) -> Tuple:
        """Get current user ID from token"""
        token = get_token_from_header()
        if not token:
            return None, self.error_response("Token is missing", 401)
        
        payload = User.verify_token(token)
        if not payload:
            return None, self.error_response("Token is invalid or expired", 401)
        
        return payload['user_id'], None
    
    def check_cold_start(self) -> Tuple:
        """Check if user needs cold start (either no preferences or < 5 preferences)"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            preference_count = UserPreference.query.filter_by(user_id=user_id).count()
            needs_cold_start = preference_count < 5
            
            return self.success_response(data={
                'needs_cold_start': needs_cold_start,
                'preference_count': preference_count,
                'minimum_required': 5
            })
            
        except Exception as e:
            return self.handle_exception(e, "Error checking cold start status")
    
    def add_preferences(self) -> Tuple:
        """Add multiple song preferences for a user (for cold start)"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            data = request.get_json()
            if not data or 'song_ids' not in data:
                return self.error_response('song_ids is required', 400)
            
            song_ids = data['song_ids']
            
            if not isinstance(song_ids, list) or len(song_ids) != 5:
                return self.error_response('Exactly 5 song IDs are required', 400)
            
            existing_songs = Music.query.filter(Music.id.in_(song_ids)).all()
            if len(existing_songs) != len(song_ids):
                return self.error_response('One or more songs not found', 404)
            
            UserPreference.query.filter_by(user_id=user_id).delete()
            
            preferences = []
            for song_id in song_ids:
                preference = UserPreference(user_id=user_id, song_id=song_id)
                db.session.add(preference)
                preferences.append(preference)
            
            db.session.commit()
            
            return self.success_response(
                data={
                    'message': 'Preferences added successfully',
                    'preferences': [pref.to_dict() for pref in preferences]
                },
                status_code=201
            )
            
        except Exception as e:
            db.session.rollback()
            return self.handle_exception(e, "Error adding preferences")
    
    def get_preferences(self) -> Tuple:
        """Get all preferences for the current user"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            preferences = UserPreference.query.filter_by(user_id=user_id).all()
            preferences_data = [pref.to_dict() for pref in preferences]
            
            return self.success_response(data=preferences_data)
            
        except Exception as e:
            return self.handle_exception(e, "Error fetching preferences")
    
    def add_preference(self) -> Tuple:
        """Add a single song preference"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            data = request.get_json()
            if not data or 'song_id' not in data:
                return self.error_response('song_id is required', 400)
            
            song_id = data['song_id']
            
            song = Music.query.get(song_id)
            if not song:
                return self.error_response('Song not found', 404)
            
            existing_pref = UserPreference.query.filter_by(
                user_id=user_id, 
                song_id=song_id
            ).first()
            
            if existing_pref:
                return self.error_response('Preference already exists', 409)
            
            preference = UserPreference(user_id=user_id, song_id=song_id)
            db.session.add(preference)
            db.session.commit()
            
            return self.success_response(
                data={
                    'message': 'Preference added successfully',
                    'preference': preference.to_dict()
                },
                status_code=201
            )
            
        except Exception as e:
            db.session.rollback()
            return self.handle_exception(e, "Error adding preference")
    
    def remove_preference(self) -> Tuple:
        """Remove a song preference"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            data = request.get_json()
            if not data or 'song_id' not in data:
                return self.error_response('song_id is required', 400)
            
            song_id = data['song_id']
            
            preference = UserPreference.query.filter_by(
                user_id=user_id, 
                song_id=song_id
            ).first()
            
            if not preference:
                return self.error_response('Preference not found', 404)
            
            db.session.delete(preference)
            db.session.commit()
            
            return self.success_response(message='Preference removed successfully')
            
        except Exception as e:
            db.session.rollback()
            return self.handle_exception(e, "Error removing preference")
    
    def get_favourites_playlist(self) -> Tuple:
        """Get user's favourites playlist containing all songs from user_preferences"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            preferences = UserPreference.query.filter_by(user_id=user_id).order_by(UserPreference.created_at.asc()).all()
            
            favourite_songs = []
            for pref in preferences:
                if pref.song:
                    song_data = pref.song.to_dict()
                    song_data['added_to_favourites'] = pref.created_at.isoformat() if pref.created_at else None
                    favourite_songs.append(song_data)
            
            playlist_data = {
                'id': 'favourites',
                'title': 'Favourites',
                'description': f'Your favorite songs ({len(favourite_songs)} tracks)',
                'song_count': len(favourite_songs),
                'songs': favourite_songs,
                'color': 'hsl(340, 70%, 50%)',
                'type': 'favourites'
            }
            
            return self.success_response(data=playlist_data)
            
        except Exception as e:
            return self.handle_exception(e, "Error fetching favourites playlist")
    
    def create_preference(self) -> Tuple:
        """Create or update user preference"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            validated_data, error_response = self.validate_json_data(self.preference_create_schema)
            if error_response:
                return error_response
            
            preference = self.preference_service.create_or_update_preference(
                user_id=user_id,
                track_id=validated_data['track_id'],
                preference_type=validated_data['preference_type']
            )
            
            preference_data = self.preference_schema.dump(preference)
            return self.success_response(
                data={'preference': preference_data},
                message="Preference saved successfully",
                status_code=201
            )
            
        except Exception as e:
            return self.handle_exception(e, "Error saving preference")
    
    def get_user_preferences(self) -> Tuple:
        """Get all preferences for current user"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            preference_type = request.args.get('type')
            preferences = self.preference_service.get_user_preferences(user_id, preference_type)
            
            preferences_data = [self.preference_schema.dump(pref) for pref in preferences]
            return self.success_response(data={'preferences': preferences_data})
            
        except Exception as e:
            return self.handle_exception(e, "Error fetching preferences")
    
    def get_user_liked_tracks(self) -> Tuple:
        """Get user's liked tracks"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            liked_tracks = self.preference_service.get_user_liked_tracks(user_id)
            return self.success_response(data={'liked_tracks': liked_tracks})
            
        except Exception as e:
            return self.handle_exception(e, "Error fetching liked tracks")
    
    def get_user_disliked_tracks(self) -> Tuple:
        """Get user's disliked tracks"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            disliked_tracks = self.preference_service.get_user_disliked_tracks(user_id)
            return self.success_response(data={'disliked_tracks': disliked_tracks})
            
        except Exception as e:
            return self.handle_exception(e, "Error fetching disliked tracks")
    
    def get_preference_stats(self) -> Tuple:
        """Get user's preference statistics"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            stats = self.preference_service.get_preference_stats(user_id)
            return self.success_response(data={'stats': stats})
            
        except Exception as e:
            return self.handle_exception(e, "Error fetching preference stats")
    
    def delete_preference(self, track_id: str) -> Tuple:
        """Delete user preference for a track"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            success = self.preference_service.remove_preference(user_id, track_id)
            if success:
                return self.success_response(message="Preference deleted successfully")
            else:
                return self.error_response("Preference not found", 404)
            
        except Exception as e:
            return self.handle_exception(e, "Error deleting preference") 