from typing import List, Optional, Dict, Any
from ..models.user_preference import UserPreference
from .base_service import BaseService

class PreferenceService(BaseService):
    """Service for user preference-related business logic"""
    
    def __init__(self):
        super().__init__(UserPreference)
    
    def create_or_update_preference(self, user_id: int, track_id: str, preference_type: str) -> UserPreference:
        """Create or update user preference for a track"""
        existing_preference = UserPreference.query.filter_by(
            user_id=user_id, 
            track_id=track_id
        ).first()
        
        if existing_preference:
            existing_preference.preference_type = preference_type
            self.db.session.commit()
            return existing_preference
        else:
            preference_data = {
                'user_id': user_id,
                'track_id': track_id,
                'preference_type': preference_type
            }
            return self.create(preference_data)
    
    def get_user_preferences(self, user_id: int, preference_type: str = None) -> List[UserPreference]:
        """Get user preferences, optionally filtered by type"""
        query = UserPreference.query.filter_by(user_id=user_id)
        if preference_type:
            query = query.filter_by(preference_type=preference_type)
        return query.all()
    
    def get_user_liked_tracks(self, user_id: int) -> List[str]:
        """Get list of track IDs that user liked"""
        preferences = self.get_user_preferences(user_id, 'like')
        return [pref.track_id for pref in preferences]
    
    def get_user_disliked_tracks(self, user_id: int) -> List[str]:
        """Get list of track IDs that user disliked"""
        preferences = self.get_user_preferences(user_id, 'dislike')
        return [pref.track_id for pref in preferences]
    
    def get_user_skipped_tracks(self, user_id: int) -> List[str]:
        """Get list of track IDs that user skipped"""
        preferences = self.get_user_preferences(user_id, 'skip')
        return [pref.track_id for pref in preferences]
    
    def remove_preference(self, user_id: int, track_id: str) -> bool:
        """Remove user preference for a track"""
        preference = UserPreference.query.filter_by(
            user_id=user_id, 
            track_id=track_id
        ).first()
        
        if preference:
            return self.delete(preference)
        return False
    
    def get_preference_by_user_and_track(self, user_id: int, track_id: str) -> Optional[UserPreference]:
        """Get specific preference by user and track"""
        return UserPreference.query.filter_by(
            user_id=user_id, 
            track_id=track_id
        ).first()
    
    def get_preference_stats(self, user_id: int) -> Dict[str, int]:
        """Get user's preference statistics"""
        preferences = self.get_user_preferences(user_id)
        stats = {'like': 0, 'dislike': 0, 'skip': 0}
        
        for pref in preferences:
            if pref.preference_type in stats:
                stats[pref.preference_type] += 1
        
        return stats
    
    def to_dict(self, preference: UserPreference) -> Dict[str, Any]:
        """Convert preference to dictionary"""
        return preference.to_dict() 