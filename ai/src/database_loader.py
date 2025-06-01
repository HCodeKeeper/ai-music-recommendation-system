"""
Database loader for AI recommender system.
Fetches music data directly from the database using SQLAlchemy.
"""
import pandas as pd
import sqlite3
import os
from typing import Tuple

def load_music_data_from_db(prioritize_playable: bool = False) -> pd.DataFrame:
    """
    Load music data directly from the SQLite database.
    Returns a DataFrame in the same format as the original CSV.
    
    Args:
        prioritize_playable: If True, prioritize songs with pathToTrack (playable songs)
    """
    # Get the database path (same as Flask app uses)
    backend_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        'backend'
    )
    
    # Database path matches Flask app configuration
    db_path = os.path.join(backend_path, 'instance', 'music_app.db')
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}. Please ensure the Flask app has been run at least once to create the database.")
    
    try:
        # Connect directly to SQLite database
        conn = sqlite3.connect(db_path)
        
        # Query all music records with optional prioritization
        if prioritize_playable:
            query = """
            SELECT 
                id as track_id,
                name,
                artist,
                genre,
                year,
                bpm as tempo,
                energy,
                danceability,
                loudness,
                liveness,
                valence,
                duration * 1000 as duration_ms,
                acousticness,
                instrumentalness,
                key,
                mode,
                speechiness,
                time_signature,
                pathToTrack,
                CASE 
                    WHEN pathToTrack IS NOT NULL AND pathToTrack != '' THEN 1
                    ELSE 0
                END as is_playable
            FROM music
            ORDER BY is_playable DESC, id
            """
        else:
            query = """
            SELECT 
                id as track_id,
                name,
                artist,
                genre,
                year,
                bpm as tempo,
                energy,
                danceability,
                loudness,
                liveness,
                valence,
                duration * 1000 as duration_ms,
                acousticness,
                instrumentalness,
                key,
                mode,
                speechiness,
                time_signature,
                pathToTrack
            FROM music
            """
        
        # Load data into DataFrame
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            raise ValueError("No music records found in database")
        
        # Convert year to int where possible
        df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
        
        if prioritize_playable:
            playable_count = df['is_playable'].sum()
            print(f"Loaded {len(df)} music records from database ({playable_count} playable)")
        else:
            print(f"Loaded {len(df)} music records from database")
        
        return df
        
    except Exception as e:
        raise RuntimeError(f"Error loading data from database: {e}")

def get_database_music_data(prioritize_playable: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Get music data from database and return both raw and encoded DataFrames.
    This replaces the CSV-based data loading.
    
    Args:
        prioritize_playable: If True, prioritize songs with pathToTrack (playable songs)
    """
    from preprocess import DataPreprocessor
    
    # Load raw data from database
    raw_df = load_music_data_from_db(prioritize_playable)
    
    # Process the data using the existing preprocessor
    preprocessor = DataPreprocessor()
    _, encoded_df = preprocessor.fit_transform_dataframe(raw_df)
    
    return raw_df, encoded_df 