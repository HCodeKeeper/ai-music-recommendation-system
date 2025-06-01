import sys
from pathlib import Path

from config import DATA_PATH_MUSIC_INFO, K_NEIGHBORS
from preprocess import DataPreprocessor
from recommender import SimilarItemRecommender


def build_model() -> SimilarItemRecommender:
    """Build and return a model ready for predictions."""
    pre = DataPreprocessor()
    raw_df, encoded_df = pre.fit_transform(DATA_PATH_MUSIC_INFO)
    model = SimilarItemRecommender(k=K_NEIGHBORS)
    model.train(raw_df, encoded_df)
    return model


def cli():
    if len(sys.argv) < 2:
        print("Usage: python main.py <seed_track_id> [options]")
        print("\nOptions:")
        print("  --diverse       Use diverse recommendations")
        print("  --skip <id>     Add track ID to skipped list")
        print("  --clear-skips   Clear the skipped tracks list")
        sys.exit(1)

    args = sys.argv[1:]
    seed_id = args[0]
    diverse_mode = "--diverse" in args
    clear_skips = "--clear-skips" in args
    
    # Build model
    try:
        model = build_model()
        
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