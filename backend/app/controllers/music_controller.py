from typing import Tuple, List, Dict, Any
from flask import request, send_file
from sqlalchemy import func, desc, case, not_, and_, or_
from ..services.music_service import MusicService
from ..services.ai_service import AIService
from ..services.preference_service import PreferenceService
from ..schemas.music_schema import MusicSchema
from ..utils.decorators import get_token_from_header
from ..models.user import User
from ..models.music import Music
from ..models.user_preference import UserPreference
from .. import db
import os
from .base_controller import BaseController

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

class MusicController(BaseController):
    """Controller for music-related operations"""
    
    def __init__(self):
        super().__init__()
        self.music_service = MusicService()
        self.ai_service = AIService()
        self.preference_service = PreferenceService()
        self.music_schema = MusicSchema()
    
    def get_current_user_id(self) -> Tuple:
        """Get current user ID from token"""
        token = get_token_from_header()
        if not token:
            return None, self.error_response("Token is missing", 401)
        
        payload = User.verify_token(token)
        if not payload:
            return None, self.error_response("Token is invalid or expired", 401)
        
        return payload['user_id'], None
    
    def check_minimum_preferences(self, user_id: int) -> Tuple:
        """Check if user has minimum required preferences (5)"""
        preference_count = UserPreference.query.filter_by(user_id=user_id).count()
        
        if preference_count < 5:
            return None, self.error_response(
                "You need at least 5 favorite songs to use this feature. Please complete the setup process.",
                400,
                {
                    'error': 'Insufficient preferences',
                    'needs_cold_start': True,
                    'preference_count': preference_count,
                    'minimum_required': 5
                }
            )
        
        return True, None
    
    def format_musical_key_ua(self, key, mode):
        """Format musical key in Ukrainian"""
        if key is None or mode is None:
            return None
        
        key_name = MUSICAL_KEYS_UA.get(key, 'Невідомо')
        mode_name = 'мажор' if mode == 1 else 'мінор'
        
        return f"{key_name} {mode_name}"
    
    def get_all_music(self) -> Tuple:
        """Get all music with pagination"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)
            
            pagination = self.music_service.paginate(page=page, per_page=per_page)
            
            music_data = [self.music_schema.dump(music) for music in pagination.items]
            
            return self.success_response(data={
                'music': music_data,
                'pagination': {
                    'page': pagination.page,
                    'pages': pagination.pages,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            })
            
        except Exception as e:
            return self.handle_exception(e, "Error fetching music")
    
    def get_random_songs(self) -> Tuple:
        """Get random songs, prioritizing songs that have MP3 files available"""
        try:
            count = int(request.args.get('count', 20))
            exclude_ids = request.args.get('exclude', '').split(',')
            exclude_ids = [id for id in exclude_ids if id]
            playable_only = request.args.get('playable_only', '').lower() == 'true'
            
            priority = case(
                (and_(Music.pathToTrack.isnot(None), Music.genre.isnot(None)), 2),
                (Music.pathToTrack.isnot(None), 1),
                else_=0
            )
            
            query = Music.query
            if exclude_ids:
                query = query.filter(not_(Music.id.in_(exclude_ids)))
            
            if playable_only:
                query = query.filter(Music.pathToTrack.isnot(None))
            
            songs = query.order_by(desc(priority), func.random()).limit(count).all()
            
            return self.success_response(data=[song.to_dict() for song in songs])
            
        except Exception as e:
            return self.handle_exception(e, "Error fetching random songs")
    
    def get_song_file(self, song_id: str) -> Tuple:
        """Serve the MP3 file for a song"""
        try:
            song = Music.query.get_or_404(song_id)
            if not song.pathToTrack:
                return self.error_response('No MP3 file available for this song', 404)
            
            mp3_root = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                'ai', 'assets', 'MP3-Example'
            )
            file_path = os.path.join(mp3_root, song.pathToTrack)
            
            if not os.path.exists(file_path):
                return self.error_response('MP3 file not found', 404)
                
            return send_file(file_path, mimetype='audio/mpeg')
            
        except Exception as e:
            return self.handle_exception(e, "Error serving song file")
    
    def get_tags(self) -> Tuple:
        """Get list of all tags with their song counts, prioritizing tags with playable songs"""
        try:
            tags = db.session.query(
                Music.genre,
                func.count(Music.id).label('count'),
                func.count(case((Music.pathToTrack.isnot(None), 1))).label('playable_count')
            ).filter(
                Music.genre.isnot(None)
            ).group_by(
                Music.genre
            ).order_by(
                desc('playable_count'),
                desc('count')
            ).all()
            
            tags_data = [{
                'name': tag,
                'count': count,
                'playable_count': playable_count,
                'color': f'hsl({hash(tag) % 360}, 70%, 50%)'
            } for tag, count, playable_count in tags if tag]
            
            return self.success_response(data=tags_data)
            
        except Exception as e:
            return self.handle_exception(e, "Error fetching tags")
    
    def get_song_details(self, song_id: str) -> Tuple:
        """Get detailed information about a specific song"""
        try:
            song = Music.query.get_or_404(song_id)
            details = song.to_dict()
            
            if song.tags:
                tag_list = [tag.strip() for tag in song.tags.split(',')]
                details['formatted_tags'] = {
                    'Настрій': next((tag for tag in tag_list if 'mood:' in tag.lower()), None),
                    'Епоха': next((tag for tag in tag_list if 'era:' in tag.lower()), None),
                    'Уд/хв': str(int(song.bpm)) if song.bpm else None,
                    'Тональність': self.format_musical_key_ua(song.key, song.mode),
                    'Енергія': 'Висока' if song.energy and song.energy > 0.66 else 'Середня' if song.energy and song.energy > 0.33 else 'Низька',
                    'Танцювальність': 'Висока' if song.danceability and song.danceability > 0.66 else 'Середня' if song.danceability and song.danceability > 0.33 else 'Низька'
                }
            
            return self.success_response(data=details)
            
        except Exception as e:
            return self.handle_exception(e, "Error fetching song details")
    
    def search_music(self) -> Tuple:
        """Search music by query"""
        try:
            query = request.args.get('q', '').strip()
            if not query:
                return self.success_response(data=[])
            
            limit = min(request.args.get('limit', 20, type=int), 100)
            
            pattern = f'%{query}%'
            
            songs = Music.query.filter(
                or_(
                    Music.name.ilike(pattern),
                    Music.artist.ilike(pattern),
                    Music.genre.ilike(pattern)
                )
            ).order_by(
                case(
                    (and_(Music.pathToTrack.isnot(None), Music.genre.isnot(None)), 2),
                    (Music.pathToTrack.isnot(None), 1),
                    else_=0
                ).desc(),
                Music.name
            ).limit(limit).all()
            
            return self.success_response(data=[song.to_dict() for song in songs])
            
        except Exception as e:
            return self.handle_exception(e, "Error searching music")
    
    def get_daily_mix(self) -> Tuple:
        """Get daily mix playlist based on user's most recent preference or specified seed"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            has_prefs, error_response = self.check_minimum_preferences(user_id)
            if error_response:
                return error_response
            
            exclude_param = request.args.get('exclude', '')
            exclude_ids = [id.strip() for id in exclude_param.split(',') if id.strip()] if exclude_param else []
            
            seed_song_id = request.args.get('seed_id')
            seed_song = None
            
            if seed_song_id:
                seed_song = Music.query.get(seed_song_id)
                if not seed_song:
                    return self.error_response(f'Specified seed song {seed_song_id} not found', 404)
                    
                user_has_song = UserPreference.query.filter_by(
                    user_id=user_id, 
                    song_id=seed_song_id
                ).first()
                
                if not user_has_song:
                    print(f"DEBUG: User {user_id} using non-preference song {seed_song_id} as seed")
            else:
                latest_preference = UserPreference.query.filter_by(
                    user_id=user_id
                ).order_by(desc(UserPreference.created_at)).first()
                
                if not latest_preference:
                    return self.error_response('No preferences found. Please complete cold start first.', 404)
                
                seed_song_id = latest_preference.song_id
                seed_song = latest_preference.song
            
            explanations = self.ai_service.get_recommendations_with_explanations(
                seed_song_id, 
                n_neighbors=7, 
                prioritize_playable=True,
                exclude_track_ids=exclude_ids
            )
            
            if not explanations:
                print("No playable AI recommendations found, trying without playability filter...")
                explanations = self.ai_service.get_recommendations_with_explanations(
                    seed_song_id, 
                    n_neighbors=7, 
                    prioritize_playable=False,
                    exclude_track_ids=exclude_ids
                )
            
            if explanations:
                recommendations = [exp['song_id'] for exp in explanations]
                recommended_songs = Music.query.filter(Music.id.in_(recommendations)).all()
                song_dict = {song.id: song for song in recommended_songs}
                ordered_songs = [song_dict[song_id] for song_id in recommendations if song_id in song_dict]
                
                print(f"DEBUG: Daily mix seed song: '{seed_song.name}' by {seed_song.artist} (ID: {seed_song_id})")
                
                songs_with_explanations = []
                distances = [exp.get('distance', 0) for exp in explanations]
                similarities = [exp.get('similarity_score', 0) for exp in explanations]
                
                for i, song in enumerate(ordered_songs):
                    song_data = song.to_dict()
                    if i < len(explanations):
                        song_data['recommendation_explanation'] = {
                            'seed_song': explanations[i]['seed_song'],
                            'seed_artist': explanations[i]['seed_artist'],
                            'similarity_score': explanations[i]['similarity_score'],
                            'features': explanations[i]['explanation_features']
                        }
                    songs_with_explanations.append(song_data)
                
                if distances:
                    avg_distance = sum(distances) / len(distances)
                    min_distance = min(distances)
                    max_distance = max(distances)
                    avg_similarity = sum(similarities) / len(similarities)
                    print(f"DEBUG: Similarity stats - Avg Distance: {avg_distance:.4f}, Min: {min_distance:.4f}, Max: {max_distance:.4f}, Avg Similarity: {avg_similarity:.4f}")
                
                return self.success_response(data={
                    'seed_song': seed_song.to_dict() if seed_song else None,
                    'recommendations': songs_with_explanations,
                    'method': 'ai_recommender',
                    'ai_available': True
                })
            
            print(f"AI recommender not available, using database fallback. Error: {self.ai_service.get_load_error()}")
            
            if not seed_song:
                seed_song = Music.query.get(seed_song_id)
            if not seed_song:
                return self.error_response('Seed song not found', 404)
                
            similar_songs = Music.query.filter(
                and_(
                    Music.id != seed_song_id,
                    or_(
                        Music.genre == seed_song.genre,
                        and_(
                            Music.energy.between(seed_song.energy - 0.2, seed_song.energy + 0.2) if seed_song.energy else True,
                            Music.danceability.between(seed_song.danceability - 0.2, seed_song.danceability + 0.2) if seed_song.danceability else True
                        )
                    )
                )
            ).order_by(
                case(
                    (and_(Music.pathToTrack.isnot(None), Music.genre.isnot(None)), 2),
                    (Music.pathToTrack.isnot(None), 1),
                    else_=0
                ).desc(),
                func.random()
            ).limit(7).all()
            
            return self.success_response(data={
                'seed_song': seed_song.to_dict(),
                'recommendations': [song.to_dict() for song in similar_songs],
                'method': 'database_fallback',
                'ai_available': self.ai_service.is_available(),
                'error': 'AI recommender unavailable, using database fallback'
            })
            
        except Exception as e:
            return self.handle_exception(e, "Error generating daily mix")
    
    def get_ai_status(self) -> Tuple:
        """Get the status of the AI recommender model"""
        try:
            return self.success_response(data={
                'available': self.ai_service.is_available(),
                'load_error': self.ai_service.get_load_error()
            })
        except Exception as e:
            return self.handle_exception(e, "Error getting AI status")
    
    def reload_ai_model(self) -> Tuple:
        """Reload the AI recommender model (admin function)"""
        try:
            self.ai_service.reload_model()
            
            return self.success_response(data={
                'success': True,
                'available': self.ai_service.is_available(),
                'message': 'AI model reload initiated'
            })
        except Exception as e:
            return self.handle_exception(e, "Error reloading AI model")
    
    def get_music_by_genre(self, genre: str) -> Tuple:
        """Get music by genre"""
        try:
            limit = min(request.args.get('limit', 20, type=int), 100)
            
            if not genre.strip():
                return self.error_response('Genre parameter is required', 400)
            
            songs = Music.query.filter(
                Music.genre == genre
            ).order_by(
                case(
                    (and_(Music.pathToTrack.isnot(None), Music.genre.isnot(None)), 2),
                    (Music.pathToTrack.isnot(None), 1),
                    else_=0
                ).desc(),
                func.random()
            ).limit(limit).all()
            
            if not songs:
                return self.error_response(f'No songs found for genre: {genre}', 404)
            
            return self.success_response(data=[song.to_dict() for song in songs])
            
        except Exception as e:
            return self.handle_exception(e, "Error fetching music by genre")
    
    def get_genre_recommendations_from_favorites(self) -> Tuple:
        """Get recommendations based on user's favorites with the same genre"""
        try:
            user_id, error_response = self.get_current_user_id()
            if error_response:
                return error_response
            
            has_prefs, error_response = self.check_minimum_preferences(user_id)
            if error_response:
                return error_response
            
            genre = request.args.get('genre', '').strip()
            limit = int(request.args.get('limit', 20))
            
            if not genre:
                return self.error_response('Genre parameter is required', 400)
            
            favorite_genre_songs = db.session.query(Music).join(
                UserPreference, Music.id == UserPreference.song_id
            ).filter(
                UserPreference.user_id == user_id,
                Music.genre == genre
            ).all()
            
            if not favorite_genre_songs:
                return self.error_response(f'No favorite songs found in {genre} genre', 404)
            
            if not self.ai_service.is_available():
                return self.error_response('AI recommender not available', 503)
            
            all_recommendations = []
            recommendation_scores = {}
            recommendation_explanations = {}
            
            for favorite_song in favorite_genre_songs:
                try:
                    explanations = self.ai_service.get_recommendations_with_explanations(
                        favorite_song.id, 
                        n_neighbors=7,
                        prioritize_playable=True
                    )
                    
                    if explanations:
                        for exp in explanations:
                            song_id = exp['song_id']
                            similarity_score = exp.get('similarity_score', 0)
                            
                            if song_id in recommendation_scores:
                                if similarity_score > recommendation_scores[song_id]:
                                    recommendation_scores[song_id] = similarity_score
                                    recommendation_explanations[song_id] = exp
                            else:
                                recommendation_scores[song_id] = similarity_score
                                recommendation_explanations[song_id] = exp
                                all_recommendations.append(song_id)
                except Exception as e:
                    print(f"Error getting recommendations for song {favorite_song.id}: {e}")
                    continue
            
            if not all_recommendations:
                return self.error_response(f'No recommendations found based on your {genre} favorites', 404)
            
            sorted_recommendations = sorted(
                all_recommendations, 
                key=lambda song_id: recommendation_scores[song_id], 
                reverse=True
            )[:limit]
            
            recommended_songs = Music.query.filter(Music.id.in_(sorted_recommendations)).all()
            song_dict = {song.id: song for song in recommended_songs}
            ordered_songs = [song_dict[song_id] for song_id in sorted_recommendations if song_id in song_dict]
            
            songs_with_explanations = []
            for song in ordered_songs:
                song_data = song.to_dict()
                song_data['similarity_score'] = recommendation_scores.get(song.id, 0)
                
                if song.id in recommendation_explanations:
                    exp = recommendation_explanations[song.id]
                    song_data['recommendation_explanation'] = {
                        'seed_song': exp['seed_song'],
                        'seed_artist': exp['seed_artist'],
                        'similarity_score': exp['similarity_score'],
                        'features': exp['explanation_features']
                    }
                
                songs_with_explanations.append(song_data)
            
            print(f"Generated {len(ordered_songs)} recommendations for {genre} based on {len(favorite_genre_songs)} favorite songs")
            
            return self.success_response(data={
                'recommendations': songs_with_explanations,
                'favorite_seeds': [song.to_dict() for song in favorite_genre_songs],
                'method': 'ai_recommender',
                'genre': genre
            })
            
        except Exception as e:
            return self.handle_exception(e, "Error getting genre recommendations from favorites") 