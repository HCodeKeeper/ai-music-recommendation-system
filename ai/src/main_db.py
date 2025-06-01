"""
Database-based AI recommender system.
Builds the model using data from the Flask app's database instead of CSV files.
"""
import sys
from pathlib import Path

from config import K_NEIGHBORS
from database_loader import get_database_music_data
from recommender import SimilarItemRecommender


def build_model_from_db(prioritize_playable: bool = False) -> SimilarItemRecommender:
    """Build and return a model ready for predictions using database data."""
    try:
        print("Loading music data from database...")
        raw_df, encoded_df = get_database_music_data(prioritize_playable=prioritize_playable)
        
        print(f"Building AI model with {len(raw_df)} songs...")
        model = SimilarItemRecommender(k=K_NEIGHBORS)
        model.train(raw_df, encoded_df)
        
        print("✓ AI model built successfully from database!")
        return model
        
    except Exception as e:
        print(f"❌ Error building model from database: {e}")
        raise


def cli():
    """Command line interface for testing the database-based recommender."""
    if len(sys.argv) < 2:
        print("Usage: python main_db.py <seed_track_id> [options]")
        print("\nOptions:")
        print("  --diverse       Use diverse recommendations")
        print("  --skip <id>     Add track ID to skipped list")
        print("  --clear-skips   Clear the skipped tracks list")
        sys.exit(1)

    args = sys.argv[1:]
    seed_id = args[0]
    diverse_mode = "--diverse" in args
    clear_skips = "--clear-skips" in args
    
    # Build model from database
    try:
        model = build_model_from_db()
        
        # Handle skipped tracks
        if clear_skips:
            model.clear_skipped()
            print("Cleared skipped tracks list")
            
        skip_idx = -1
        while True:
            try:
                skip_idx = args.index("--skip", skip_idx + 1)
                if skip_idx + 1 < len(args):
                    track_id = args[skip_idx + 1]
                    model.add_to_skipped(track_id)
                    print(f"Added {track_id} to skipped tracks")
            except ValueError:
                break
        
        # Show recommendations
        model.visualize(seed_id, diverse=diverse_mode)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli() 