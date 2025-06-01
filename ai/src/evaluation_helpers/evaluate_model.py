# -*- coding: utf-8 -*-
"""
Offline evaluation script for the **SimilarItemRecommender**
-----------------------------------------------------------
Evaluates Precision@k, Recall@k, MAP@k and Hit‑Rate@k using
*intrinsic* item‑item relevance rules:
    • same_artist          (exact artist match)
    • same_genre           (exact genre match)
    • same_audio_features  (energy, danceability, valence within ±0.15)

Usage (from project root):
    python evaluate_model.py --k 10 --max-seeds 10000

Requires the existing modules:
    - config.py
    - database_loader.py  (or any DataFrame with song metadata)
    - preprocess.py       (DataPreprocessor class)
    - recommender.py      (SimilarItemRecommender class)
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

from ..config import K_NEIGHBORS
from ..database_loader import get_database_music_data
from ..recommender import SimilarItemRecommender

# Set style for better-looking plots
plt.style.use('default')
sns.set_palette("husl")

# ------------------------------------------------------------------
# 1.  RULE DEFINITIONS
# ------------------------------------------------------------------

def same_artist(a: dict, b: dict) -> bool:
    """Check if two songs have the same artist."""
    return a.get("artist") and a["artist"] == b["artist"]

def same_genre(a: dict, b: dict) -> bool:
    """Check if two songs have the same genre."""
    return a.get("genre") and a["genre"] == b["genre"]

def same_audio_features(a: dict, b: dict, eps: float = 0.15,
                         feats: tuple[str, ...] = ("energy", "danceability", "valence")) -> bool:
    """Check if two songs have similar audio features within epsilon tolerance."""
    try:
        return all(abs(float(a[f]) - float(b[f])) <= eps for f in feats)
    except (KeyError, TypeError, ValueError):
        return False

# Available rules mapping
AVAILABLE_RULES = {
    'artist': same_artist,
    'genre': same_genre,
    'audio': same_audio_features
}

def get_active_rules(rule_flags: Dict[str, bool]) -> List:
    """Get list of active rules based on command line flags."""
    active_rules = []
    
    if rule_flags.get('artist', False):
        active_rules.append(AVAILABLE_RULES['artist'])
    if rule_flags.get('genre', False):
        active_rules.append(AVAILABLE_RULES['genre'])
    if rule_flags.get('audio', False):
        active_rules.append(AVAILABLE_RULES['audio'])
    
    # If no rules specified, use all rules (default behavior)
    if not active_rules:
        active_rules = list(AVAILABLE_RULES.values())
    
    return active_rules

def is_relevant(seed_row: dict, cand_row: dict, active_rules: List) -> bool:
    """Return True if ANY active rule fires."""
    return any(rule(seed_row, cand_row) for rule in active_rules)

def get_rules_description(rule_flags: Dict[str, bool]) -> str:
    """Get human-readable description of active rules."""
    active_rule_names = []
    
    if rule_flags.get('artist', False):
        active_rule_names.append("same_artist")
    if rule_flags.get('genre', False):
        active_rule_names.append("same_genre")  
    if rule_flags.get('audio', False):
        active_rule_names.append("similar_audio_features")
    
    # If no rules specified, show default
    if not active_rule_names:
        active_rule_names = ["same_artist", "same_genre", "similar_audio_features"]
    
    return " OR ".join(active_rule_names)

# ------------------------------------------------------------------
# 2.  BUILD RELEVANCE DICTIONARY
# ------------------------------------------------------------------

def build_relevance_sets(raw_df: pd.DataFrame, rule_flags: Dict[str, bool], max_tracks: int | None = None) -> Dict[str, Set[str]]:
    """Return mapping track_id → {relevant track_ids}."""
    # Sample tracks if max_tracks is specified
    if max_tracks and len(raw_df) > max_tracks:
        print(f"Sampling {max_tracks} tracks from {len(raw_df)} total tracks for faster evaluation...")
        raw_df = raw_df.sample(n=max_tracks, random_state=42).reset_index(drop=True)
    
    records = raw_df.to_dict("records")
    id2row = {str(row["track_id"]): row for row in records}
    
    # Get active rules based on flags
    active_rules = get_active_rules(rule_flags)
    rules_desc = get_rules_description(rule_flags)
    
    relevance: Dict[str, Set[str]] = {tid: set() for tid in id2row}

    # Quadratic nested loop – complexity O(n²)
    total_comparisons = len(records) * len(records)
    print(f"Building relevance sets for {len(records)} tracks ({total_comparisons:,} comparisons)...")
    print(f"Active relevance rules: {rules_desc}")
    
    for seed in tqdm(records, desc="Building relevance sets", unit="tracks"):
        sid = str(seed["track_id"])
        for cand in records:
            cid = str(cand["track_id"])
            if sid == cid:
                continue
            if is_relevant(seed, cand, active_rules):
                relevance[sid].add(cid)
    
    # Print some statistics
    non_empty_relevance = sum(1 for rel_set in relevance.values() if rel_set)
    avg_relevance = np.mean([len(rel_set) for rel_set in relevance.values()])
    print(f"Relevance statistics: {non_empty_relevance}/{len(relevance)} tracks have relevant items")
    print(f"Average relevance set size: {avg_relevance:.2f} tracks")
    
    return relevance

# ------------------------------------------------------------------
# 3.  METRIC COMPUTATION
# ------------------------------------------------------------------

def average_precision_at_k(recs: List[str], relevant: Set[str], k: int) -> float:
    """Calculate Average Precision@k for a single recommendation list."""
    hits, ap = 0, 0.0
    for rank, r in enumerate(recs[:k], 1):
        if r in relevant:
            hits += 1
            ap += hits / rank
    denom = min(len(relevant), k)
    return ap / denom if denom else 0.0


def evaluate_model(model: SimilarItemRecommender,
                   relevance: Dict[str, Set[str]],
                   k: int = 10,
                   seed_sample: int | None = None) -> Dict[str, float]:
    """Evaluate the model using intrinsic relevance rules."""
    seeds = list(relevance.keys())
    if seed_sample and seed_sample < len(seeds):
        random.shuffle(seeds)
        seeds = seeds[:seed_sample]

    prec = rec = ap = hr = 0.0
    n_eval = 0

    print(f"Evaluating model on {len(seeds)} seed tracks...")
    for sid in tqdm(seeds, desc="Evaluating", unit="seeds"):
        rel_set = relevance[sid]
        if not rel_set:
            continue  # skip seeds with empty ground truth
        
        try:
            recs = model.get_recommendations(sid, n_neighbors=k)
            if not recs:
                continue
                
            # Convert recommendations to strings for consistency
            recs = [str(r) for r in recs]
            
            hits = len(set(recs) & rel_set)
            prec += hits / k
            rec  += hits / len(rel_set)
            ap   += average_precision_at_k(recs, rel_set, k)
            hr   += 1 if hits else 0
            n_eval += 1
        except Exception as e:
            # Skip tracks that cause errors (e.g., not found in dataset)
            continue

    if n_eval == 0:
        print("Warning: No tracks could be evaluated!")
        return {m: 0.0 for m in ["precision", "recall", "map", "hit_rate", "evaluated"]}

    return {
        "precision": prec / n_eval,
        "recall":    rec  / n_eval,
        "map":       ap   / n_eval,
        "hit_rate":  hr   / n_eval,
        "evaluated": n_eval,
    }

# ------------------------------------------------------------------
# 4.  VISUALIZATION FUNCTIONS
# ------------------------------------------------------------------

def plot_evaluation_results(metrics: Dict[str, float], k: int, save_path: str = "evaluation_results.png"):
    """Create a comprehensive visualization of evaluation results."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'Recommender System Evaluation Results (k={k})', fontsize=16, fontweight='bold')
    
    # 1. Main metrics bar chart
    metric_names = ['Precision', 'Recall', 'MAP', 'Hit Rate']
    metric_values = [metrics['precision'], metrics['recall'], metrics['map'], metrics['hit_rate']]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    bars = ax1.bar(metric_names, metric_values, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
    ax1.set_title('Overall Performance Metrics', fontweight='bold')
    ax1.set_ylabel('Score')
    ax1.set_ylim(0, 1.0)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, metric_values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # 2. Metrics comparison radar chart (simplified as line plot)
    angles = np.linspace(0, 2 * np.pi, len(metric_names), endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle
    values = metric_values + [metric_values[0]]  # Complete the circle
    
    ax2.plot(angles, values, 'o-', linewidth=2, color='#FF6B6B', markersize=8)
    ax2.fill(angles, values, alpha=0.25, color='#FF6B6B')
    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(metric_names)
    ax2.set_ylim(0, 1)
    ax2.set_title('Performance Radar', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. Evaluation summary
    ax3.axis('off')
    summary_text = f"""
    📊 EVALUATION SUMMARY
    
    🎵 Tracks Evaluated: {metrics['evaluated']:,}
    🎯 Precision@{k}: {metrics['precision']:.1%}
    🔍 Recall@{k}: {metrics['recall']:.1%}
    📈 MAP@{k}: {metrics['map']:.1%}
    ✅ Hit Rate@{k}: {metrics['hit_rate']:.1%}
    
    📋 Interpretation:
    • Precision: {get_precision_interpretation(metrics['precision'])}
    • Recall: {get_recall_interpretation(metrics['recall'])}
    • Hit Rate: {get_hitrate_interpretation(metrics['hit_rate'])}
    """
    ax3.text(0.05, 0.95, summary_text, transform=ax3.transAxes, fontsize=11,
             verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
    
    # 4. Performance grade
    overall_score = (metrics['precision'] + metrics['recall'] + metrics['map'] + metrics['hit_rate']) / 4
    grade, grade_color = get_performance_grade(overall_score)
    
    ax4.pie([overall_score, 1-overall_score], labels=['Performance', 'Room for Improvement'], 
            colors=[grade_color, '#E0E0E0'], startangle=90, counterclock=False)
    ax4.set_title(f'Overall Grade: {grade}\n({overall_score:.1%})', fontweight='bold', color=grade_color)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"📈 Evaluation charts saved to: {save_path}")
    return fig

def plot_relevance_distribution(relevance: Dict[str, Set[str]], save_path: str = "relevance_distribution.png"):
    """Plot distribution of relevance set sizes."""
    relevance_sizes = [len(rel_set) for rel_set in relevance.values()]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Relevance Set Analysis', fontsize=14, fontweight='bold')
    
    # Histogram
    ax1.hist(relevance_sizes, bins=50, alpha=0.7, color='#4ECDC4', edgecolor='white')
    ax1.set_xlabel('Number of Relevant Tracks')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Distribution of Relevance Set Sizes')
    ax1.grid(axis='y', alpha=0.3)
    
    # Box plot
    ax2.boxplot(relevance_sizes, patch_artist=True, 
                boxprops=dict(facecolor='#4ECDC4', alpha=0.7),
                medianprops=dict(color='red', linewidth=2))
    ax2.set_ylabel('Number of Relevant Tracks')
    ax2.set_title('Relevance Set Size Distribution')
    ax2.grid(axis='y', alpha=0.3)
    
    # Add statistics
    stats_text = f"""Statistics:
    Mean: {np.mean(relevance_sizes):.1f}
    Median: {np.median(relevance_sizes):.1f}
    Max: {np.max(relevance_sizes)}
    Min: {np.min(relevance_sizes)}"""
    
    ax2.text(1.1, 0.7, stats_text, transform=ax2.transAxes, fontsize=10,
             bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"📊 Relevance distribution chart saved to: {save_path}")
    return fig

def get_precision_interpretation(precision: float) -> str:
    """Get interpretation for precision score."""
    if precision >= 0.3: return "Excellent"
    elif precision >= 0.2: return "Good"
    elif precision >= 0.1: return "Fair"
    else: return "Needs Improvement"

def get_recall_interpretation(recall: float) -> str:
    """Get interpretation for recall score."""
    if recall >= 0.5: return "Excellent"
    elif recall >= 0.3: return "Good"
    elif recall >= 0.15: return "Fair"
    else: return "Needs Improvement"

def get_hitrate_interpretation(hitrate: float) -> str:
    """Get interpretation for hit rate score."""
    if hitrate >= 0.8: return "Excellent"
    elif hitrate >= 0.6: return "Good"
    elif hitrate >= 0.4: return "Fair"
    else: return "Needs Improvement"

def get_performance_grade(score: float) -> tuple[str, str]:
    """Get letter grade and color for overall performance."""
    if score >= 0.4: return "A", "#4CAF50"
    elif score >= 0.3: return "B", "#8BC34A"
    elif score >= 0.2: return "C", "#FFC107"
    elif score >= 0.1: return "D", "#FF9800"
    else: return "F", "#F44336"

# ------------------------------------------------------------------
# 5.  MAIN CLI
# ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Offline evaluation for item‑based k‑NN recommender")
    parser.add_argument("--k", type=int, default=K_NEIGHBORS, help="length of recommendation list")
    parser.add_argument("--max-seeds", type=int, default=None, help="evaluate on at most N seed tracks for speed")
    parser.add_argument("--max-tracks", type=int, default=2000, help="use at most N tracks for evaluation (default: 2000)")
    parser.add_argument("--playable-only", action="store_true", help="train playable‑only sub‑model as well")
    parser.add_argument("--prioritize-playable", action="store_true", help="prioritize playable recommendations")
    parser.add_argument("--rule-artist", action="store_true", help="use same artist relevance rule")
    parser.add_argument("--rule-genre", action="store_true", help="use same genre relevance rule")
    parser.add_argument("--rule-audio", action="store_true", help="use similar audio features relevance rule")
    args = parser.parse_args()

    # Parse rule flags
    rule_flags = {
        'artist': args.rule_artist,
        'genre': args.rule_genre,
        'audio': args.rule_audio
    }

    print("\n🔄  Loading catalogue from database …")
    try:
        raw_df, encoded_df = get_database_music_data(prioritize_playable=args.playable_only)
        print(f"   → {len(raw_df):,} tracks loaded\n")
    except Exception as e:
        print(f"Error loading data from database: {e}")
        return

    # Ensure track_id is string type for consistency
    raw_df["track_id"] = raw_df["track_id"].astype(str)
    encoded_df["track_id"] = encoded_df["track_id"].astype(str)

    print("🤖  Training item‑based k‑NN model …")
    rec = SimilarItemRecommender(k=args.k)
    rec.train(raw_df, encoded_df)
    print("   → Model training complete\n")

    print("📚  Building relevance sets …")
    relevance = build_relevance_sets(raw_df, rule_flags=rule_flags, max_tracks=args.max_tracks)
    print("   → Relevance sets built\n")

    print("📏  Running evaluation …")
    metrics = evaluate_model(rec, relevance, k=args.k, seed_sample=args.max_seeds)

    print("\n=====  RESULTS  =====")
    print(f"Rules used               : {get_rules_description(rule_flags)}")
    print(f"Seeds evaluated          : {metrics['evaluated']:,}")
    print(f"Precision@{args.k:<2}         : {metrics['precision']:.3f}")
    print(f"Recall@{args.k:<2}            : {metrics['recall']:.3f}")
    print(f"MAP@{args.k:<2}               : {metrics['map']:.3f}")
    print(f"Hit‑Rate@{args.k:<2}          : {metrics['hit_rate']:.3f}\n")
    
    # Additional analysis
    if metrics['evaluated'] > 0:
        print("=====  ANALYSIS  =====")
        total_relevant = sum(len(rel_set) for rel_set in relevance.values())
        print(f"Total relevant pairs     : {total_relevant:,}")
        print(f"Avg relevant per track   : {total_relevant/len(relevance):.2f}")
        
        # Show some example recommendations for analysis
        print("\n=====  SAMPLE RECOMMENDATIONS  =====")
        sample_tracks = random.sample(list(relevance.keys()), min(3, len(relevance)))
        for track_id in sample_tracks:
            if relevance[track_id]:  # Only show tracks with ground truth
                try:
                    recs = rec.get_recommendations(track_id, n_neighbors=5)
                    if recs:
                        track_info = raw_df[raw_df['track_id'] == track_id].iloc[0]
                        print(f"\nSeed: {track_info['name']} - {track_info['artist']} ({track_info.get('genre', 'N/A')})")
                        print(f"Ground truth relevant: {len(relevance[track_id])} tracks")
                        
                        hits = set(str(r) for r in recs) & relevance[track_id]
                        print(f"Recommendations (hits: {len(hits)}/5):")
                        for i, rec_id in enumerate(recs, 1):
                            rec_info = raw_df[raw_df['track_id'] == str(rec_id)]
                            if not rec_info.empty:
                                rec_row = rec_info.iloc[0]
                                hit_marker = "✓" if str(rec_id) in relevance[track_id] else "✗"
                                print(f"  {i}. {hit_marker} {rec_row['name']} - {rec_row['artist']} ({rec_row.get('genre', 'N/A')})")
                except Exception as e:
                    continue

    # Plot evaluation results with rule information in filename
    rules_suffix = "_".join([rule for rule, active in rule_flags.items() if active])
    if not rules_suffix:  # If no specific rules, use "all"
        rules_suffix = "all"
    
    # Create results directory if it doesn't exist
    results_dir = Path("new_eval_results")
    results_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_filename = results_dir / f"evaluation_results_{rules_suffix}_{timestamp}.png"
    relevance_filename = results_dir / f"relevance_distribution_{rules_suffix}_{timestamp}.png"
    
    plot_evaluation_results(metrics, args.k, save_path=str(results_filename))
    plot_relevance_distribution(relevance, save_path=str(relevance_filename))


if __name__ == "__main__":
    main()
