from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from typing import List, Dict, Set, Tuple

# Ukrainian translations for recommendation explanations
UKRAINIAN_TRANSLATIONS = {
    'same_genre': 'Той самий жанр ({genre})',
    'same_artist': 'Той самий виконавець ({artist})',
    'similar_era': 'Схожа епоха ({year})',
    'similar_tempo': 'Схожий темп (~{tempo} Уд/хв)',
    'unknown': 'Невідомо',
    'audio_features': {
        'energy': 'енергійність',
        'danceability': 'танцювальність',
        'valence': 'позитивність',
        'acousticness': 'акустичність',
        'instrumentalness': 'інструментальність'
    },
    'feature_levels': {
        'high': 'висока',
        'medium': 'середня',
        'low': 'низька'
    },
    'similar_feature': 'Схожа {feature} ({level})'
}

class SimilarItemRecommender:
    def __init__(self, k: int = 7):
        self.k = k
        self.knn: NearestNeighbors | None = None
        self.knn_playable: NearestNeighbors | None = None  # Separate k-NN for playable songs only
        self.raw_df: pd.DataFrame | None = None
        self.encoded_df: pd.DataFrame | None = None
        self.playable_encoded_df: pd.DataFrame | None = None  # Encoded data for playable songs only
        self.skipped_songs: Set[str] = set()  # Track IDs that user has skipped
        
    def train(self, raw_df: pd.DataFrame, encoded_df: pd.DataFrame):
        self.raw_df = raw_df.copy()
        self.encoded_df = encoded_df.copy()
        
        # Train main k-NN model (all songs)
        features = self.encoded_df.drop(columns=['track_id'])
        self.knn = NearestNeighbors(n_neighbors=self.k, metric='euclidean')
        self.knn.fit(features)
        
        # Create playable-only dataset and train separate k-NN model
        if 'pathToTrack' in self.raw_df.columns:
            # Filter to only playable songs (pathToTrack is not null and not empty)
            playable_mask = self.raw_df['pathToTrack'].notna() & (self.raw_df['pathToTrack'] != '')
            playable_raw = self.raw_df[playable_mask].copy()
            
            if len(playable_raw) > 0:
                # Get corresponding encoded data for playable songs
                playable_track_ids = set(playable_raw['track_id'])
                playable_encoded_mask = self.encoded_df['track_id'].isin(playable_track_ids)
                self.playable_encoded_df = self.encoded_df[playable_encoded_mask].copy().reset_index(drop=True)
                
                # Train k-NN model on playable songs only
                playable_features = self.playable_encoded_df.drop(columns=['track_id'])
                self.knn_playable = NearestNeighbors(n_neighbors=min(self.k, len(playable_features)), metric='euclidean')
                self.knn_playable.fit(playable_features)
                
                print(f"Trained playable-only k-NN model with {len(playable_features)} songs")
            else:
                print("No playable songs found, playable-only model not available")

    def add_to_skipped(self, track_ids: str | List[str]):
        """Add track(s) to skipped list."""
        if isinstance(track_ids, str):
            track_ids = [track_ids]
        self.skipped_songs.update(track_ids)

    def clear_skipped(self):
        """Clear the list of skipped tracks."""
        self.skipped_songs.clear()

    def get_recommendations(self, track_id: str, n_neighbors: int | None = None, include_distances: bool = False, prioritize_playable: bool = False) -> List[str] | Tuple[List[str], np.ndarray]:
        """Get recommendations, optionally with distances and playability priority."""
        if self.knn is None:
            raise RuntimeError("Model not trained yet.")
            
        n = n_neighbors or self.k
        
        # Check if we want playable songs and if the seed song is in the playable dataset
        if prioritize_playable and self.knn_playable is not None and self.playable_encoded_df is not None:
            # Check if seed song is in playable dataset
            seed_in_playable = track_id in self.playable_encoded_df['track_id'].values
            
            if seed_in_playable:
                # Use playable-only model (seed song is playable)
                knn_model = self.knn_playable
                encoded_df = self.playable_encoded_df
                print(f"DEBUG: Using playable-only k-NN model with {len(encoded_df)} songs (seed is playable)")
            else:
                # Hybrid approach: use full model but filter results to playable songs
                print(f"DEBUG: Seed song not playable, using hybrid approach (full model + playable filter)")
                print(f"DEBUG: Full dataset: {len(self.encoded_df)} songs, Playable dataset: {len(self.playable_encoded_df)} songs")
                return self._get_hybrid_playable_recommendations(track_id, n, include_distances)
        else:
            # Use full model
            knn_model = self.knn
            encoded_df = self.encoded_df
            print(f"DEBUG: Using full k-NN model with {len(encoded_df)} songs (prioritize_playable={prioritize_playable})")
        
        n_to_fetch = min(n * 3, len(encoded_df) - 1)  # Fetch more to account for skipped
        print(f"DEBUG: Fetching {n_to_fetch} neighbors to return {n} recommendations")
        
        idx_list = encoded_df.index[encoded_df['track_id'] == track_id].tolist()
        if not idx_list:
            print(f"DEBUG: Track {track_id} not found in dataset")
            return ([], np.array([])) if include_distances else []
            
        idx = idx_list[0]
        print(f"DEBUG: Found seed track at index {idx} in dataset")
        
        # Safety check: ensure we have valid data to query
        features_for_query = encoded_df.drop(columns=['track_id']).iloc[idx:idx+1]
        print(f"DEBUG: Query features shape: {features_for_query.shape}")
        
        if features_for_query.empty:
            print(f"DEBUG: Empty features for query, returning empty results")
            return ([], np.array([])) if include_distances else []
        
        distances, indices = knn_model.kneighbors(
            features_for_query, 
            n_neighbors=n_to_fetch
        )
        
        print(f"DEBUG: k-NN returned {len(indices[0])} neighbors with distances ranging from {distances[0].min():.4f} to {distances[0].max():.4f}")
        
        # Get all candidate recommendations
        rec_ids = encoded_df.iloc[indices[0]]['track_id'].tolist()
        rec_distances = distances[0]
        
        # Remove seed and skipped songs
        filtered_recs = []
        filtered_distances = []
        for rec_id, distance in zip(rec_ids, rec_distances):
            if rec_id != track_id and rec_id not in self.skipped_songs:
                filtered_recs.append(rec_id)
                filtered_distances.append(distance)
                if len(filtered_recs) >= n:
                    break
                    
        print(f"DEBUG: Returning {len(filtered_recs)} recommendations")
        if filtered_recs and self.raw_df is not None:
            print("DEBUG: Recommended songs with similarity distances:")
            for i, (rec_id, distance) in enumerate(zip(filtered_recs, filtered_distances), 1):
                song_info = self.get_track_meta(rec_id)
                similarity_score = 1 / (1 + distance)  # Convert distance to similarity (0-1)
                print(f"  {i}. {song_info.get('name', 'Unknown')} - {song_info.get('artist', 'Unknown')} (Distance: {distance:.4f}, Similarity: {similarity_score:.4f})")
        
        if include_distances:
            return filtered_recs, np.array(filtered_distances)
        return filtered_recs
    
    def _get_hybrid_playable_recommendations(self, track_id: str, n: int, include_distances: bool = False) -> List[str] | Tuple[List[str], np.ndarray]:
        """Get playable recommendations for a non-playable seed song using hybrid approach."""
        # Use full model to find neighbors, then filter to playable ones
        n_to_fetch = min(n * 10, len(self.encoded_df) - 1)  # Fetch more since we'll filter
        
        idx_list = self.encoded_df.index[self.encoded_df['track_id'] == track_id].tolist()
        if not idx_list:
            return ([], np.array([])) if include_distances else []
            
        idx = idx_list[0]
        distances, indices = self.knn.kneighbors(
            self.encoded_df.drop(columns=['track_id']).iloc[idx:idx+1], 
            n_neighbors=n_to_fetch
        )
        
        # Get all candidate recommendations
        rec_ids = self.encoded_df.iloc[indices[0]]['track_id'].tolist()
        rec_distances = distances[0]
        
        # Get set of playable track IDs for fast lookup
        playable_track_ids = set(self.playable_encoded_df['track_id']) if self.playable_encoded_df is not None else set()
        
        # Filter to playable songs only
        filtered_recs = []
        filtered_distances = []
        for rec_id, distance in zip(rec_ids, rec_distances):
            if (rec_id != track_id and 
                rec_id not in self.skipped_songs and 
                rec_id in playable_track_ids):
                filtered_recs.append(rec_id)
                filtered_distances.append(distance)
                if len(filtered_recs) >= n:
                    break
                    
        print(f"DEBUG: Hybrid approach found {len(filtered_recs)} playable recommendations")
        if filtered_recs and self.raw_df is not None:
            print("DEBUG: Hybrid recommended songs with similarity distances:")
            for i, (rec_id, distance) in enumerate(zip(filtered_recs, filtered_distances), 1):
                song_info = self.get_track_meta(rec_id)
                similarity_score = 1 / (1 + distance)  # Convert distance to similarity (0-1)
                print(f"  {i}. {song_info.get('name', 'Unknown')} - {song_info.get('artist', 'Unknown')} (Distance: {distance:.4f}, Similarity: {similarity_score:.4f})")
        
        if include_distances:
            return filtered_recs, np.array(filtered_distances)
        return filtered_recs

    def get_diverse_recommendations(self, track_id: str, n: int | None = None, prioritize_playable: bool = False) -> List[str]:
        """Get more diverse recommendations by clustering and sampling."""
        if n is None:
            n = self.k
            
        # Get more recommendations than needed with distances
        recs, distances = self.get_recommendations(track_id, n * 2, include_distances=True, prioritize_playable=prioritize_playable)
        if not recs:
            return []
            
        # Convert distances to weights (inverse distance)
        weights = 1 / (distances + 1e-6)  # Add small epsilon to avoid division by zero
        weights = weights / weights.sum()  # Normalize
        
        # Randomly sample n recommendations with weights
        if len(recs) <= n:
            return recs
            
        indices = np.random.choice(
            len(recs), size=n, replace=False, p=weights
        )
        return [recs[i] for i in indices]

    def get_track_meta(self, track_id: str) -> Dict[str, str]:
        if self.raw_df is None:
            return {}
        row = self.raw_df[self.raw_df['track_id'] == track_id]
        if row.empty:
            return {}
        r = row.iloc[0]
        return {
            'track_id': track_id,
            'name': r.get('name', ''),
            'artist': r.get('artist', ''),
            'year':  r.get('year', ''),
        }

    def get_full_recs(self, track_id: str, n: int | None = None, diverse: bool = False, prioritize_playable: bool = False):
        """Get recommendations with metadata. Use diverse=True for more variety."""
        if diverse:
            ids = self.get_diverse_recommendations(track_id, n, prioritize_playable=prioritize_playable)
        else:
            ids = self.get_recommendations(track_id, n, prioritize_playable=prioritize_playable)
        return [self.get_track_meta(i) for i in ids]

    def update(self, new_encoded: pd.DataFrame):
        """Incrementally add new songs (re‑fit knn)."""
        if self.encoded_df is None:
            raise RuntimeError("Train before update.")
        self.encoded_df = pd.concat([self.encoded_df, new_encoded], ignore_index=True)
        features = self.encoded_df.drop(columns=['track_id'])
        self.knn.fit(features)

    def visualize(self, track_id: str, diverse: bool = False):
        """Simple print‑based viz of recommendations."""
        recs = self.get_full_recs(track_id, diverse=diverse)
        if not recs:
            print("No recommendations found (all candidates may have been skipped)")
            return
            
        print(f"Seed → {self.get_track_meta(track_id)}")
        print(f"Mode → {'Diverse' if diverse else 'Standard'}")
        if self.skipped_songs:
            print(f"Skipped tracks → {len(self.skipped_songs)}")
        print()
        
        for i, rec in enumerate(recs, 1):
            print(f"{i}. {rec['artist']} – {rec['name']} ({rec['year']})")

    def get_recommendations_with_explanations(self, track_id: str, n_neighbors: int | None = None, prioritize_playable: bool = False) -> List[Dict]:
        """Get recommendations with explanations of why each song was recommended."""
        recommendations, distances = self.get_recommendations(track_id, n_neighbors, include_distances=True, prioritize_playable=prioritize_playable)
        
        if not recommendations:
            return []
        
        # Get seed song info
        seed_info = self.get_track_meta(track_id)
        
        # Create explanations for each recommendation
        explanations = []
        for rec_id, distance in zip(recommendations, distances):
            rec_info = self.get_track_meta(rec_id)
            
            # Calculate similarity features
            explanation = {
                'song_id': rec_id,
                'song_name': rec_info.get('name', UKRAINIAN_TRANSLATIONS['unknown']),
                'artist': rec_info.get('artist', UKRAINIAN_TRANSLATIONS['unknown']),
                'seed_song': seed_info.get('name', UKRAINIAN_TRANSLATIONS['unknown']),
                'seed_artist': seed_info.get('artist', UKRAINIAN_TRANSLATIONS['unknown']),
                'similarity_score': float(1 / (1 + distance)),  # Convert distance to similarity (0-1)
                'distance': float(distance),
                'explanation_features': self._get_similarity_features(track_id, rec_id)
            }
            explanations.append(explanation)
        
        return explanations
    
    def _get_similarity_features(self, seed_id: str, rec_id: str) -> List[str]:
        """Get the main features that make two songs similar."""
        if self.raw_df is None:
            return []
        
        seed_row = self.raw_df[self.raw_df['track_id'] == seed_id]
        rec_row = self.raw_df[self.raw_df['track_id'] == rec_id]
        
        if seed_row.empty or rec_row.empty:
            return []
        
        seed_data = seed_row.iloc[0]
        rec_data = rec_row.iloc[0]
        
        features = []
        
        # Check genre similarity
        if seed_data.get('genre') == rec_data.get('genre') and seed_data.get('genre'):
            features.append(UKRAINIAN_TRANSLATIONS['same_genre'].format(genre=seed_data.get('genre')))
        
        # Check artist similarity
        if seed_data.get('artist') == rec_data.get('artist'):
            features.append(UKRAINIAN_TRANSLATIONS['same_artist'].format(artist=seed_data.get('artist')))
        
        # Check year similarity (within 5 years)
        seed_year = seed_data.get('year')
        rec_year = rec_data.get('year')
        if seed_year and rec_year and abs(int(seed_year) - int(rec_year)) <= 5:
            features.append(UKRAINIAN_TRANSLATIONS['similar_era'].format(year=rec_year))
        
        # Check audio feature similarities
        audio_features = ['energy', 'danceability', 'valence', 'acousticness', 'instrumentalness']
        for feature in audio_features:
            seed_val = seed_data.get(feature)
            rec_val = rec_data.get(feature)
            if seed_val is not None and rec_val is not None:
                if abs(float(seed_val) - float(rec_val)) < 0.2:  # Similar within 0.2
                    level_en = "high" if float(rec_val) > 0.7 else "medium" if float(rec_val) > 0.3 else "low"
                    level_uk = UKRAINIAN_TRANSLATIONS['feature_levels'][level_en]
                    feature_uk = UKRAINIAN_TRANSLATIONS['audio_features'][feature]
                    features.append(UKRAINIAN_TRANSLATIONS['similar_feature'].format(feature=feature_uk, level=level_uk))
        
        # Check tempo similarity (within 20 BPM)
        seed_tempo = seed_data.get('tempo')
        rec_tempo = rec_data.get('tempo')
        if seed_tempo and rec_tempo and abs(float(seed_tempo) - float(rec_tempo)) <= 20:
            features.append(UKRAINIAN_TRANSLATIONS['similar_tempo'].format(tempo=int(float(rec_tempo))))
        
        return features[:3]  # Return top 3 most relevant features