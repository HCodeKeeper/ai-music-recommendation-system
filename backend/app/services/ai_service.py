import os
import sys
from typing import Optional, List, Dict, Any

class AIService:
    """Service for AI recommender model functionality"""
    
    def __init__(self):
        self._model = None
        self._load_error = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Ensure the model is initialized (lazy initialization)."""
        if not self._initialized:
            print("=" * 50)
            print("INITIALIZING AI RECOMMENDER MODEL (LAZY)")
            print("=" * 50)
            try:
                print("Initializing AI recommender model from database...")
                
                ai_src_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                    'ai', 'src'
                )
                
                if ai_src_path not in sys.path:
                    sys.path.insert(0, ai_src_path)
                
                from main_db import build_model_from_db
                
                self._model = build_model_from_db(prioritize_playable=False)
                self._load_error = None
                self._initialized = True
                print("AI model initialized successfully and ready for use!")
                
            except Exception as e:
                self._load_error = str(e)
                self._model = None
                self._initialized = True
                print(f"Failed to initialize AI model: {e}")
                print("Daily mix will fall back to database-based recommendations")
            print("=" * 50)
    
    def initialize_model(self, prioritize_playable: bool = False):
        """Initialize the AI model from database data. Called once during app startup."""
        if self._initialized:
            print("AI model already initialized")
            return
        self._ensure_initialized()
    
    def is_available(self) -> bool:
        """Check if the AI model is available for use."""
        self._ensure_initialized()
        return self._model is not None
    
    def get_recommendations(self, track_id: str, n_neighbors: int = 5, prioritize_playable: bool = False) -> List[Dict[str, Any]]:
        """Get recommendations using the pre-loaded AI model."""
        print(f"DEBUG: get_recommendations called for track_id={track_id}, prioritize_playable={prioritize_playable}")
        self._ensure_initialized()
        print(f"DEBUG: After _ensure_initialized, model is None: {self._model is None}")
        if self._model is None:
            print("DEBUG: Model is None, returning empty list")
            return []
        
        try:
            result = self._model.get_recommendations(track_id, n_neighbors=n_neighbors, prioritize_playable=prioritize_playable)
            print(f"DEBUG: Got {len(result)} recommendations")
            return result
        except Exception as e:
            print(f"Error getting AI recommendations: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_recommendations_with_explanations(self, track_id: str, n_neighbors: int = 5, prioritize_playable: bool = False, exclude_track_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Get recommendations with explanations using the pre-loaded AI model."""
        self._ensure_initialized()
        if self._model is None:
            return []
        
        original_skipped = self._model.skipped_songs.copy()
        if exclude_track_ids:
            self._model.add_to_skipped(exclude_track_ids)
            print(f"DEBUG: Temporarily excluding {len(exclude_track_ids)} songs from recommendations")
        
        try:
            result = self._model.get_recommendations_with_explanations(track_id, n_neighbors=n_neighbors, prioritize_playable=prioritize_playable)
            return result
        except Exception as e:
            print(f"Error getting AI recommendations with explanations: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            self._model.skipped_songs = original_skipped
    
    def get_load_error(self) -> Optional[str]:
        """Get the error message if model failed to load."""
        return self._load_error
    
    def reload_model(self):
        """Reload the model (useful after database updates)."""
        print("Reloading AI model...")
        self._model = None
        self._load_error = None
        self._initialized = False
        self.initialize_model() 