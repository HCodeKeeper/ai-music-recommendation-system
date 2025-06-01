import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def create_preferences_table():
    """Create the user_preferences table"""
    app = create_app()
    
    with app.app_context():
        
        db.create_all()
        print("User preferences table created successfully!")

if __name__ == "__main__":
    print("Creating user preferences table...")
    create_preferences_table() 