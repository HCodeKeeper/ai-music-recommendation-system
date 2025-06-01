
"""
Migration script to remove the redundant mp3_path column from the music table.
Since pathToTrack serves the same purpose and is actively used throughout the application.
"""
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def remove_mp3_path_column():
    """Remove the redundant mp3_path column from the music table"""
    app = create_app()
    
    with app.app_context():
        try:
            
            with db.engine.connect() as connection:
                result = connection.execute(text("PRAGMA table_info(music)"))
                columns = [row[1] for row in result]
                
                if 'mp3_path' in columns:
                    print("Removing mp3_path column from music table...")
                    
                    
                    
                    connection.execute(text("""
                        CREATE TABLE music_new AS 
                        SELECT 
                            id, name, artist, genre, year, bpm, energy, danceability, 
                            loudness, liveness, valence, duration, acousticness, 
                            instrumentalness, tags, key, mode, speechiness, 
                            time_signature, pathToTrack
                        FROM music
                    """))
                    
                    
                    connection.execute(text("DROP TABLE music"))
                    
                    
                    connection.execute(text("ALTER TABLE music_new RENAME TO music"))
                    
                    
                    connection.commit()
                    
                    print("✓ Successfully removed mp3_path column")
                else:
                    print("mp3_path column not found - already removed or doesn't exist")
                    
        except Exception as e:
            print(f"❌ Error removing mp3_path column: {e}")
            raise

if __name__ == "__main__":
    print("Starting migration to remove mp3_path column...")
    remove_mp3_path_column()
    print("Migration completed!") 