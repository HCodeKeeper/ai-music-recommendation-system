from typing import List, Optional, Dict, Any
from ..models.music import Music
from .base_service import BaseService

class MusicService(BaseService):
    """Service for music-related business logic"""
    
    def __init__(self):
        super().__init__(Music)
    
    def get_by_track_id(self, track_id: str) -> Optional[Music]:
        """Get music by track ID"""
        return Music.query.filter_by(track_id=track_id).first()
    
    def search_music(self, query: str, limit: int = 50) -> List[Music]:
        """Search music by title, artist, or album"""
        search_pattern = f"%{query}%"
        return Music.query.filter(
            Music.title.ilike(search_pattern) |
            Music.artist.ilike(search_pattern) |
            Music.album.ilike(search_pattern)
        ).limit(limit).all()
    
    def get_by_genre(self, genre: str, limit: int = 50) -> List[Music]:
        """Get music by genre"""
        return Music.query.filter_by(genre=genre).limit(limit).all()
    
    def get_by_artist(self, artist: str, limit: int = 50) -> List[Music]:
        """Get music by artist"""
        return Music.query.filter_by(artist=artist).limit(limit).all()
    
    def get_popular_tracks(self, limit: int = 50) -> List[Music]:
        """Get popular tracks ordered by popularity"""
        return Music.query.order_by(Music.popularity.desc()).limit(limit).all()
    
    def get_random_tracks(self, limit: int = 50) -> List[Music]:
        """Get random tracks"""
        return Music.query.order_by(self.db.func.random()).limit(limit).all()
    
    def get_similar_tracks(self, track_id: str, limit: int = 10) -> List[Music]:
        """Get tracks similar to the given track based on audio features"""
        base_track = self.get_by_track_id(track_id)
        if not base_track:
            return []
        
        return Music.query.filter(
            Music.track_id != track_id,
            Music.genre == base_track.genre
        ).order_by(
            self.db.func.abs(Music.danceability - base_track.danceability) +
            self.db.func.abs(Music.energy - base_track.energy) +
            self.db.func.abs(Music.valence - base_track.valence)
        ).limit(limit).all()
    
    def get_tracks_by_filters(self, filters: Dict[str, Any], limit: int = 50) -> List[Music]:
        """Get tracks by various filters"""
        query = Music.query
        
        if 'genre' in filters:
            query = query.filter_by(genre=filters['genre'])
        
        if 'year_min' in filters:
            query = query.filter(Music.year >= filters['year_min'])
        
        if 'year_max' in filters:
            query = query.filter(Music.year <= filters['year_max'])
        
        if 'min_popularity' in filters:
            query = query.filter(Music.popularity >= filters['min_popularity'])
        
        return query.limit(limit).all()
    
    def to_dict(self, music: Music) -> Dict[str, Any]:
        """Convert music to dictionary"""
        return music.to_dict() 