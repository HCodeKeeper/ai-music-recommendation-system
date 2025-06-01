#!/usr/bin/env python3
"""
Simple script to get 7 neighbors for a given seed track ID.
Usage: python get_neighbors.py <seed_track_id>
"""
import sys
import os

# Add the src directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)  # Go up one level to src/
root_dir = os.path.dirname(src_dir)     # Go up one more level to ai/
sys.path.insert(0, src_dir)
sys.path.insert(0, root_dir)

from config import K_NEIGHBORS
from database_loader import get_database_music_data
from recommender import SimilarItemRecommender


def build_model() -> SimilarItemRecommender:
    """Build and return a model ready for predictions."""
    print("Loading and preprocessing data from database...")
    raw_df, encoded_df = get_database_music_data()
    print(f"Loaded {len(raw_df)} tracks from database")
    
    print("Training recommendation model...")
    model = SimilarItemRecommender(k=7)  # Set to 7 neighbors as requested
    model.train(raw_df, encoded_df)
    print("Model trained successfully!")
    return model


def get_detailed_track_info(model, track_id: str) -> dict:
    """Get comprehensive track information including all features."""
    if model.raw_df is None:
        return {}
    
    row = model.raw_df[model.raw_df['track_id'] == track_id]
    if row.empty:
        return {}
    
    track_data = row.iloc[0]
    
    # Get basic info
    info = {
        'track_id': track_id,
        'name': track_data.get('name', 'Unknown'),
        'artist': track_data.get('artist', 'Unknown'),
        'year': track_data.get('year', 'Unknown'),
        'genre': track_data.get('genre', 'Unknown'),
        'tags': track_data.get('tags', 'Unknown'),
    }
    
    # Audio features
    audio_features = {
        'energy': track_data.get('energy'),
        'danceability': track_data.get('danceability'),
        'valence': track_data.get('valence'),
        'acousticness': track_data.get('acousticness'),
        'instrumentalness': track_data.get('instrumentalness'),
        'liveness': track_data.get('liveness'),
        'speechiness': track_data.get('speechiness'),
        'tempo': track_data.get('tempo'),
        'loudness': track_data.get('loudness'),
        'key': track_data.get('key'),
        'mode': track_data.get('mode'),
        'time_signature': track_data.get('time_signature'),
        'duration_ms': track_data.get('duration_ms'),
    }
    
    # Add audio features to info
    info.update(audio_features)
    
    return info


def format_audio_features(track_info: dict) -> str:
    """Format audio features for display."""
    lines = []
    
    # Group features logically
    mood_features = [
        ('Energy', track_info.get('energy'), 'Intensity and power'),
        ('Valence', track_info.get('valence'), 'Musical positivity'),
        ('Danceability', track_info.get('danceability'), 'Rhythm suitability for dancing'),
    ]
    
    character_features = [
        ('Acousticness', track_info.get('acousticness'), 'Acoustic vs electronic'),
        ('Instrumentalness', track_info.get('instrumentalness'), 'Likelihood of no vocals'),
        ('Liveness', track_info.get('liveness'), 'Presence of live audience'),
        ('Speechiness', track_info.get('speechiness'), 'Presence of spoken words'),
    ]
    
    technical_features = [
        ('Tempo', track_info.get('tempo'), 'BPM'),
        ('Loudness', track_info.get('loudness'), 'dB'),
        ('Key', track_info.get('key'), 'Musical key (0-11)'),
        ('Mode', track_info.get('mode'), '1=Major, 0=Minor'),
        ('Time Signature', track_info.get('time_signature'), 'Beats per measure'),
    ]
    
    # Format mood features
    lines.append("     🎵 Mood & Feel:")
    for name, value, desc in mood_features:
        if value is not None:
            percentage = f"{float(value) * 100:.0f}%" if 0 <= float(value) <= 1 else f"{float(value):.2f}"
            lines.append(f"        {name}: {percentage} ({desc})")
    
    # Format character features
    lines.append("     🎶 Character:")
    for name, value, desc in character_features:
        if value is not None:
            percentage = f"{float(value) * 100:.0f}%" if 0 <= float(value) <= 1 else f"{float(value):.2f}"
            lines.append(f"        {name}: {percentage} ({desc})")
    
    # Format technical features
    lines.append("     🔧 Technical:")
    for name, value, desc in technical_features:
        if value is not None:
            if name == 'Tempo':
                lines.append(f"        {name}: {float(value):.0f} {desc}")
            elif name == 'Loudness':
                lines.append(f"        {name}: {float(value):.1f} {desc}")
            elif name in ['Key', 'Mode', 'Time Signature']:
                lines.append(f"        {name}: {int(float(value))} ({desc})")
            else:
                lines.append(f"        {name}: {value} ({desc})")
    
    # Duration
    duration_ms = track_info.get('duration_ms')
    if duration_ms is not None:
        duration_sec = int(float(duration_ms)) // 1000
        minutes = duration_sec // 60
        seconds = duration_sec % 60
        lines.append(f"     ⏱️  Duration: {minutes}:{seconds:02d}")
    
    return "\n".join(lines)


def get_similarity_insights(seed_info: dict, rec_info: dict) -> str:
    """Generate insights about why a track is similar to the seed."""
    insights = []
    
    # Genre similarity
    if seed_info.get('genre') == rec_info.get('genre') and seed_info.get('genre') != 'Unknown':
        insights.append(f"🎸 Same genre ({seed_info['genre']})")
    
    # Artist similarity
    if seed_info.get('artist') == rec_info.get('artist'):
        insights.append(f"👤 Same artist ({seed_info['artist']})")
    
    # Year similarity (within 5 years)
    try:
        seed_year = int(seed_info.get('year', 0))
        rec_year = int(rec_info.get('year', 0))
        if seed_year > 0 and rec_year > 0 and abs(seed_year - rec_year) <= 5:
            insights.append(f"📅 Similar era (within 5 years)")
    except (ValueError, TypeError):
        pass
    
    # Audio feature similarities
    audio_similarities = []
    features_to_check = [
        ('energy', 'Energy level'),
        ('valence', 'Musical mood'),
        ('danceability', 'Danceability'),
        ('acousticness', 'Acoustic character'),
        ('tempo', 'Tempo')
    ]
    
    for feature, description in features_to_check:
        seed_val = seed_info.get(feature)
        rec_val = rec_info.get(feature)
        
        if seed_val is not None and rec_val is not None:
            try:
                seed_float = float(seed_val)
                rec_float = float(rec_val)
                
                if feature == 'tempo':
                    # For tempo, check within 20 BPM
                    if abs(seed_float - rec_float) <= 20:
                        audio_similarities.append(f"🎵 Similar {description.lower()}")
                else:
                    # For percentage features, check within 20%
                    if abs(seed_float - rec_float) <= 0.2:
                        audio_similarities.append(f"🎵 Similar {description.lower()}")
            except (ValueError, TypeError):
                pass
    
    # Add top 2 audio similarities
    insights.extend(audio_similarities[:2])
    
    if not insights:
        insights.append("🔍 Similar audio characteristics")
    
    return " • ".join(insights[:3])  # Show top 3 insights


def get_neighbors(seed_track_id: str) -> None:
    """Get and display 7 neighbors for the given seed track ID."""
    try:
        # Build the model
        model = build_model()
        
        # Check if the seed track exists and get detailed info
        seed_info = get_detailed_track_info(model, seed_track_id)
        if not seed_info or seed_info.get('name') == 'Unknown':
            print(f"Error: Track ID '{seed_track_id}' not found in the database.")
            print("Please provide a valid track ID.")
            return
        
        print(f"\n{'='*100}")
        print(f"🎯 SEED TRACK - YOUR REFERENCE POINT")
        print(f"{'='*100}")
        print(f"🎵 {seed_info['name']} - {seed_info['artist']}")
        print(f"📅 Year: {seed_info['year']}  |  🎸 Genre: {seed_info['genre']}")
        if seed_info.get('tags') and seed_info['tags'] != 'Unknown':
            print(f"🏷️  Tags: {seed_info['tags']}")
        print(f"🆔 Track ID: {seed_track_id}")
        print(f"📝 Use this information to compare with the recommended tracks below")
        print(format_audio_features(seed_info))
        
        # Get recommendations with distances
        recommendations = model.get_recommendations(seed_track_id, n_neighbors=7, include_distances=True)
        
        if not recommendations or len(recommendations) != 2:
            print("No recommendations found for this track.")
            return
        
        rec_ids, distances = recommendations
        
        if not rec_ids:
            print("No recommendations found for this track.")
            return
        
        print(f"\n{'='*100}")
        print(f"🎯 7 SIMILAR TRACKS TO '{seed_info['name']}' (COMPARE WITH SEED ABOVE)")
        print(f"{'='*100}")
        
        for i, (track_id, distance) in enumerate(zip(rec_ids, distances), 1):
            track_info = get_detailed_track_info(model, track_id)
            similarity_score = 1 / (1 + distance)  # Convert distance to similarity (0-1)
            similarity_insights = get_similarity_insights(seed_info, track_info)
            
            print(f"\n{'-'*100}")
            print(f"#{i:2d}. 🎵 {track_info['name']} - {track_info['artist']}")
            print(f"     📅 Year: {track_info['year']}  |  🎸 Genre: {track_info['genre']}")
            if track_info.get('tags') and track_info['tags'] != 'Unknown':
                print(f"     🏷️  Tags: {track_info['tags']}")
            print(f"     🆔 Track ID: {track_id}")
            print(f"     📊 Similarity: {similarity_score:.1%} (Distance: {distance:.2f})")
            print(f"     🔗 Why similar: {similarity_insights}")
            print(format_audio_features(track_info))
        
        print(f"\n{'='*100}")
        print(f"💡 TIP: Compare the audio features above with your seed track to understand the similarities!")
        print(f"{'='*100}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return


def main():
    """Main CLI function."""
    if len(sys.argv) != 2:
        print("Usage: python get_neighbors.py <seed_track_id>")
        print("\nExample:")
        print("  python get_neighbors.py 4uLU6hMCjMI75M1A2tKUQC")
        sys.exit(1)
    
    seed_track_id = sys.argv[1].strip()
    if not seed_track_id:
        print("Error: Please provide a non-empty track ID.")
        sys.exit(1)
    
    get_neighbors(seed_track_id)


if __name__ == "__main__":
    main() 