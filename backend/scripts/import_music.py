import pandas as pd
import os
import sys
from pathlib import Path


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.music import Music

def find_mp3_path(track_id, mp3_root):
    """Find MP3 file path for a given track ID by scanning all subdirectories"""
    for root, _, files in os.walk(mp3_root):
        for file in files:
            if file.endswith('.mp3') and track_id in file:
                
                rel_path = os.path.relpath(os.path.join(root, file), mp3_root)
                return rel_path.replace('\\', '/')  
    return None

def extract_genre_from_tags(tags_str):
    """Extract genre from tags field - use first tag value if comma-delimited, or the tag itself if not"""
    if not tags_str or pd.isna(tags_str):
        return None
    
    tags_str = str(tags_str).strip()
    if not tags_str:
        return None
    
    
    if ',' in tags_str:
        
        first_tag = tags_str.split(',')[0].strip()
        
        if first_tag.startswith('"') and first_tag.endswith('"'):
            first_tag = first_tag[1:-1].strip()
        return first_tag if first_tag else None
    else:
        
        if tags_str.startswith('"') and tags_str.endswith('"'):
            tags_str = tags_str[1:-1].strip()
        return tags_str if tags_str else None

def import_music_data(csv_path, mp3_root):
    """Import music data from CSV and add MP3 paths"""
    app = create_app()
    
    with app.app_context():
        
        Music.query.delete()
        db.session.commit()
        
        print("Reading CSV file...")
        
        chunk_size = 1000
        chunks = pd.read_csv(csv_path, chunksize=chunk_size)
        
        total_records = 0
        tags_extracted = 0
        tag_examples = []
        
        for chunk in chunks:
            print(f"Processing chunk {total_records // chunk_size + 1}...")
            
            for _, row in chunk.iterrows():
                
                mp3_path = find_mp3_path(row['track_id'], mp3_root)
                
                
                genre = extract_genre_from_tags(row['tags'])
                
                
                if genre:
                    tags_extracted += 1
                    if len(tag_examples) < 10:  
                        tag_examples.append({
                            'track': row['name'],
                            'artist': row['artist'],
                            'original_tags': row['tags'],
                            'extracted_tag': genre
                        })
                
                
                music = Music(
                    id=row['track_id'],
                    name=row['name'],
                    artist=row['artist'],
                    genre=genre,
                    year=str(row['year']) if pd.notna(row['year']) else None,
                    bpm=float(row['tempo']) if pd.notna(row['tempo']) else None,
                    energy=float(row['energy']) if pd.notna(row['energy']) else None,
                    danceability=float(row['danceability']) if pd.notna(row['danceability']) else None,
                    loudness=float(row['loudness']) if pd.notna(row['loudness']) else None,
                    liveness=float(row['liveness']) if pd.notna(row['liveness']) else None,
                    valence=float(row['valence']) if pd.notna(row['valence']) else None,
                    duration=float(row['duration_ms']) / 1000 if pd.notna(row['duration_ms']) else None,  
                    acousticness=float(row['acousticness']) if pd.notna(row['acousticness']) else None,
                    instrumentalness=float(row['instrumentalness']) if pd.notna(row['instrumentalness']) else None,
                    
                    tags=row['tags'] if pd.notna(row['tags']) else None,
                    key=int(row['key']) if pd.notna(row['key']) else None,
                    mode=int(row['mode']) if pd.notna(row['mode']) else None,
                    speechiness=float(row['speechiness']) if pd.notna(row['speechiness']) else None,
                    time_signature=int(row['time_signature']) if pd.notna(row['time_signature']) else None,
                    
                    pathToTrack=mp3_path
                )
                db.session.add(music)
                
                total_records += 1
                if total_records % 1000 == 0:
                    print(f"Processed {total_records} records...")
                    
                    db.session.commit()
            
        
        db.session.commit()
        
        
        print(f"\nTag Extraction Results:")
        print(f"Total records: {total_records}")
        print(f"Tags extracted: {tags_extracted}")
        print(f"Tag extraction rate: {(tags_extracted/total_records)*100:.1f}%")
        
        print(f"\nFirst {len(tag_examples)} tag extraction examples:")
        for i, example in enumerate(tag_examples, 1):
            print(f"{i}. {example['track']} - {example['artist']}")
            print(f"   Tags: {example['original_tags']}")
            print(f"   Extracted Tag: {example['extracted_tag']}")
            print()
        
        print(f"Completed! Imported {total_records} records.")

def test_tag_extraction():
    """Test the tag extraction function with various tag formats"""
    test_cases = [
        ('"rock", "classic rock", "70s"', 'rock'),
        ('rock, classic rock, 70s', 'rock'),
        ('"pop"', 'pop'),
        ('jazz', 'jazz'),
        ('', None),
        (None, None),
        ('"electronic", "dance", "edm"', 'electronic'),
        ('hip-hop, rap, urban', 'hip-hop'),
        ('"country music"', 'country music'),
        ('alternative rock, indie, 90s', 'alternative rock')
    ]
    
    print("Testing tag extraction function:")
    for tags, expected in test_cases:
        result = extract_genre_from_tags(tags)
        status = "✓" if result == expected else "✗"
        print(f"{status} Tags: {tags} → Primary Tag: {result} (expected: {expected})")
    print()

if __name__ == "__main__":
    
    test_tag_extraction()
    
    
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(current_dir)
    
    csv_path = os.path.join(project_root, 'ai', 'assets', 'Music Info.csv')
    mp3_root = os.path.join(project_root, 'ai', 'assets', 'MP3-Example')
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)
        
    if not os.path.exists(mp3_root):
        print(f"Error: MP3 directory not found at {mp3_root}")
        sys.exit(1)
    
    print("Starting music data import...")
    print(f"CSV file: {csv_path}")
    print(f"MP3 root directory: {mp3_root}")
    
    import_music_data(csv_path, mp3_root) 