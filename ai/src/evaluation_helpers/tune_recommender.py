"""
Hyperparameter tuning script for the **SimilarItemRecommender**
===============================================================
Grid/random search optimization for the item-based k-NN recommender using
the same intrinsic relevance rules as evaluate_model.py.

Parameters explored:
    • k_neighbors      : [5, 7, 10, 15, 20]
    • metric           : ["euclidean", "manhattan", "cosine"]
    • audio_multiplier : [0.5, 1.0, 1.5, 2.0]   (scales all audio feature weights)
    • genre_weight     : [25, 50, 75, 100]
    • artist_weight    : [50, 100, 150, 200]

Usage:
    python tune_recommender.py --trials 50 --jobs 4 --search random
    python tune_recommender.py --search grid  # full grid search
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

from ..config import (
    K_NEIGHBORS, GENRE_WEIGHT, ARTIST_WEIGHT,
    DURATION_MS_WEIGHT, DANCEABILITY_WEIGHT, ENERGY_WEIGHT, KEY_WEIGHT,
    LOUDNESS_WEIGHT, MODE_WEIGHT, SPEECHINESS_WEIGHT, ACOUSTICNESS_WEIGHT,
    INSTRUMENTALNESS_WEIGHT, LIVENESS_WEIGHT, VALENCE_WEIGHT, TEMPO_WEIGHT,
    TIME_SIGNATURE_WEIGHT
)
from ..database_loader import get_database_music_data
from ..preprocess import DataPreprocessor
from ..recommender import SimilarItemRecommender
from .evaluate_model import build_relevance_sets, evaluate_model, get_active_rules

# Audio feature columns that can be scaled
AUDIO_FEATURES = [
    'duration_ms', 'danceability', 'energy', 'key', 'loudness', 'mode',
    'speechiness', 'acousticness', 'instrumentalness', 'liveness',
    'valence', 'tempo', 'time_signature'
]

# Base weights for scaling
AUDIO_BASE_WEIGHTS = {
    'duration_ms': DURATION_MS_WEIGHT,
    'danceability': DANCEABILITY_WEIGHT,
    'energy': ENERGY_WEIGHT,
    'key': KEY_WEIGHT,
    'loudness': LOUDNESS_WEIGHT,
    'mode': MODE_WEIGHT,
    'speechiness': SPEECHINESS_WEIGHT,
    'acousticness': ACOUSTICNESS_WEIGHT,
    'instrumentalness': INSTRUMENTALNESS_WEIGHT,
    'liveness': LIVENESS_WEIGHT,
    'valence': VALENCE_WEIGHT,
    'tempo': TEMPO_WEIGHT,
    'time_signature': TIME_SIGNATURE_WEIGHT,
}

# Search space definition
SEARCH_SPACE = {
    "k_neighbors":      [5, 7, 10, 15, 20],
    "metric":           ["euclidean", "manhattan", "cosine"],
    "audio_multiplier": [0.5, 1.0, 1.5, 2.0],
    "genre_weight":     [25, 50, 75, 100],
    "artist_weight":    [50, 100, 150, 200],
}

@dataclass
class TrialResult:
    """Result of a single hyperparameter trial."""
    params: Dict
    map_score: float
    precision: float
    recall: float
    hit_rate: float
    evaluated: int
    duration: float
    trial_id: int

class CustomDataPreprocessor(DataPreprocessor):
    """Extended preprocessor that allows custom weight overrides."""
    
    def __init__(self, custom_weights: Dict[str, float] = None, **kwargs):
        super().__init__(**kwargs)
        self.custom_weights = custom_weights or {}
    
    def fit_transform_dataframe(self, raw_df: pd.DataFrame):
        """Override to apply custom weights."""
        # Get the normal preprocessing
        raw_df_out, encoded_df = super().fit_transform_dataframe(raw_df)
        
        # Apply custom weights if specified
        if self.custom_weights:
            # Apply audio feature weight multiplier
            if 'audio_multiplier' in self.custom_weights:
                multiplier = self.custom_weights['audio_multiplier']
                for feature in AUDIO_FEATURES:
                    if feature in encoded_df.columns:
                        base_weight = AUDIO_BASE_WEIGHTS.get(feature, 1.0)
                        # Remove old weight and apply new weight
                        encoded_df[feature] = (encoded_df[feature] / base_weight) * (base_weight * multiplier)
            
            # Apply genre weight override
            if 'genre_weight' in self.custom_weights:
                new_weight = self.custom_weights['genre_weight']
                for col in self.genre_dummy_cols:
                    if col in encoded_df.columns:
                        # Remove old weight and apply new weight
                        encoded_df[col] = (encoded_df[col] / GENRE_WEIGHT) * new_weight
            
            # Apply artist weight override
            if 'artist_weight' in self.custom_weights:
                new_weight = self.custom_weights['artist_weight']
                if self.artist_col in encoded_df.columns:
                    # Remove old weight and apply new weight
                    encoded_df[self.artist_col] = (encoded_df[self.artist_col] / ARTIST_WEIGHT) * new_weight
        
        return raw_df_out, encoded_df

class TunableRecommender(SimilarItemRecommender):
    """Extended recommender that allows metric parameter changes."""
    
    def __init__(self, k: int = 7, metric: str = "euclidean"):
        super().__init__(k)
        self.metric = metric
    
    def train(self, raw_df: pd.DataFrame, encoded_df: pd.DataFrame):
        """Train with specified metric."""
        self.raw_df = raw_df.copy()
        self.encoded_df = encoded_df.copy()
        
        # Train main k-NN model with custom metric
        features = self.encoded_df.drop(columns=['track_id'])
        self.knn = NearestNeighbors(n_neighbors=self.k, metric=self.metric)
        self.knn.fit(features)
        
        # Train playable-only model if applicable
        if 'pathToTrack' in self.raw_df.columns:
            playable_mask = self.raw_df['pathToTrack'].notna() & (self.raw_df['pathToTrack'] != '')
            playable_raw = self.raw_df[playable_mask].copy()
            
            if len(playable_raw) > 0:
                playable_track_ids = set(playable_raw['track_id'])
                playable_encoded_mask = self.encoded_df['track_id'].isin(playable_track_ids)
                self.playable_encoded_df = self.encoded_df[playable_encoded_mask].copy().reset_index(drop=True)
                
                playable_features = self.playable_encoded_df.drop(columns=['track_id'])
                self.knn_playable = NearestNeighbors(
                    n_neighbors=min(self.k, len(playable_features)), 
                    metric=self.metric
                )
                self.knn_playable.fit(playable_features)

def run_single_trial(raw_df: pd.DataFrame, 
                    relevance: Dict[str, Set[str]], 
                    rule_flags: Dict[str, bool],
                    params: Dict, 
                    k_eval: int, 
                    seed_sample: int,
                    trial_id: int) -> TrialResult:
    """Run a single hyperparameter trial."""
    start_time = time.time()
    
    try:
        # 1. Create custom preprocessor with weight overrides
        preprocessor = CustomDataPreprocessor(custom_weights=params)
        _, encoded_df = preprocessor.fit_transform_dataframe(raw_df)
        
        # 2. Train recommender with custom parameters
        recommender = TunableRecommender(
            k=params["k_neighbors"], 
            metric=params["metric"]
        )
        recommender.train(raw_df, encoded_df)
        
        # 3. Evaluate performance
        metrics = evaluate_model(
            recommender, 
            relevance, 
            k=k_eval, 
            seed_sample=seed_sample
        )
        
        duration = time.time() - start_time
        
        return TrialResult(
            params=params,
            map_score=metrics["map"],
            precision=metrics["precision"],
            recall=metrics["recall"],
            hit_rate=metrics["hit_rate"],
            evaluated=metrics["evaluated"],
            duration=duration,
            trial_id=trial_id
        )
        
    except Exception as e:
        print(f"Trial {trial_id} failed: {e}")
        duration = time.time() - start_time
        return TrialResult(
            params=params,
            map_score=0.0,
            precision=0.0,
            recall=0.0,
            hit_rate=0.0,
            evaluated=0,
            duration=duration,
            trial_id=trial_id
        )

def generate_parameter_combinations(search_space: Dict, 
                                  n_trials: int = None, 
                                  search_type: str = "grid",
                                  random_seed: int = 42) -> List[Dict]:
    """Generate parameter combinations for search."""
    # Generate all possible combinations
    keys = list(search_space.keys())
    values = list(search_space.values())
    all_combinations = list(itertools.product(*values))
    
    # Convert to list of dictionaries
    param_list = [dict(zip(keys, combo)) for combo in all_combinations]
    
    if search_type == "random" and n_trials and n_trials < len(param_list):
        # Random sampling
        random.Random(random_seed).shuffle(param_list)
        param_list = param_list[:n_trials]
    elif search_type == "grid":
        # Use all combinations
        pass
    
    return param_list

def save_results(results: List[TrialResult], output_dir: Path):
    """Save tuning results to files."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create detailed results DataFrame
    results_data = []
    for r in results:
        row = {
            'trial_id': r.trial_id,
            'map_score': r.map_score,
            'precision': r.precision,
            'recall': r.recall,
            'hit_rate': r.hit_rate,
            'evaluated': r.evaluated,
            'duration_seconds': r.duration,
            **r.params
        }
        results_data.append(row)
    
    results_df = pd.DataFrame(results_data)
    
    # Save CSV
    csv_path = output_dir / f"tuning_results_{timestamp}.csv"
    results_df.to_csv(csv_path, index=False)
    
    # Save best parameters as JSON
    best_result = max(results, key=lambda x: x.map_score)
    best_params_path = output_dir / f"best_params_{timestamp}.json"
    
    best_summary = {
        'best_params': best_result.params,
        'performance': {
            'map_score': best_result.map_score,
            'precision': best_result.precision,
            'recall': best_result.recall,
            'hit_rate': best_result.hit_rate,
            'evaluated': best_result.evaluated
        },
        'search_info': {
            'total_trials': len(results),
            'total_time_minutes': sum(r.duration for r in results) / 60,
            'timestamp': timestamp
        }
    }
    
    with open(best_params_path, 'w') as f:
        json.dump(best_summary, f, indent=2)
    
    return csv_path, best_params_path, best_result

def main():
    parser = argparse.ArgumentParser(description="Hyperparameter tuning for SimilarItemRecommender")
    parser.add_argument("--k-eval", type=int, default=10, help="k for evaluation metrics")
    parser.add_argument("--trials", type=int, default=None, help="number of random trials (default = full grid)")
    parser.add_argument("--jobs", type=int, default=-1, help="parallel workers (-1 = all cores)")
    parser.add_argument("--seed-sample", type=int, default=1000, help="number of seeds to evaluate per trial")
    parser.add_argument("--max-tracks", type=int, default=2000, help="subset catalogue for relevance building")
    parser.add_argument("--search", choices=["grid", "random"], default="random", help="search strategy")
    parser.add_argument("--rule-artist", action="store_true", help="use same artist relevance rule")
    parser.add_argument("--rule-genre", action="store_true", help="use same genre relevance rule")
    parser.add_argument("--rule-audio", action="store_true", help="use similar audio features relevance rule")
    parser.add_argument("--random-seed", type=int, default=42, help="random seed for reproducibility")
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.random_seed)
    np.random.seed(args.random_seed)
    
    # Parse rule flags
    rule_flags = {
        'artist': args.rule_artist,
        'genre': args.rule_genre,
        'audio': args.rule_audio
    }
    
    print("🔄 Loading catalogue from database...")
    raw_df, _ = get_database_music_data(prioritize_playable=False)
    raw_df["track_id"] = raw_df["track_id"].astype(str)
    print(f"   → {len(raw_df):,} tracks loaded")
    
    print("📚 Building relevance sets...")
    relevance = build_relevance_sets(raw_df, rule_flags, max_tracks=args.max_tracks)
    print(f"   → Relevance sets built for {len(relevance)} tracks")
    
    # Generate parameter combinations
    param_combinations = generate_parameter_combinations(
        SEARCH_SPACE, 
        n_trials=args.trials, 
        search_type=args.search,
        random_seed=args.random_seed
    )
    
    print(f"🔬 Running {args.search} search with {len(param_combinations)} parameter combinations...")
    print(f"   → Using {args.jobs} parallel workers")
    print(f"   → Evaluating {args.seed_sample} seeds per trial")
    
    # Create output directory
    output_dir = Path("new_eval_results")
    output_dir.mkdir(exist_ok=True)
    
    # Run parallel trials
    start_time = time.time()
    
    # Use threading backend to avoid Windows multiprocessing issues
    results = Parallel(n_jobs=args.jobs, verbose=1, backend='threading')(
        delayed(run_single_trial)(
            raw_df, relevance, rule_flags, params, args.k_eval, args.seed_sample, i
        )
        for i, params in enumerate(param_combinations)
    )
    
    total_time = time.time() - start_time
    
    # Filter out failed trials
    successful_results = [r for r in results if r.evaluated > 0]
    
    if not successful_results:
        print("❌ No successful trials! Check your parameters and data.")
        return
    
    # Sort by MAP score
    successful_results.sort(key=lambda x: x.map_score, reverse=True)
    
    # Save results
    csv_path, json_path, best_result = save_results(successful_results, output_dir)
    
    # Print summary
    print(f"\n🏆 TUNING COMPLETE")
    print(f"   → Total time: {total_time/60:.1f} minutes")
    print(f"   → Successful trials: {len(successful_results)}/{len(param_combinations)}")
    print(f"   → Results saved to: {csv_path}")
    print(f"   → Best params saved to: {json_path}")
    
    print(f"\n🥇 BEST CONFIGURATION:")
    print(json.dumps(best_result.params, indent=2))
    print(f"\n📊 BEST PERFORMANCE:")
    print(f"   MAP@{args.k_eval}:       {best_result.map_score:.4f}")
    print(f"   Precision@{args.k_eval}: {best_result.precision:.4f}")
    print(f"   Recall@{args.k_eval}:    {best_result.recall:.4f}")
    print(f"   Hit Rate@{args.k_eval}:  {best_result.hit_rate:.4f}")
    print(f"   Seeds evaluated:         {best_result.evaluated:,}")
    print(f"   Trial duration:          {best_result.duration:.1f}s")
    
    # Show top 5 results
    print(f"\n🔝 TOP 5 CONFIGURATIONS:")
    for i, result in enumerate(successful_results[:5], 1):
        print(f"{i}. MAP: {result.map_score:.4f} | k={result.params['k_neighbors']}, "
              f"metric={result.params['metric']}, audio_mult={result.params['audio_multiplier']}")

if __name__ == "__main__":
    main() 