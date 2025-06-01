from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv
from .config import get_config


load_dotenv()


db = SQLAlchemy()

def create_app(config_name=None):
    app = Flask(__name__)
    
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    

    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": [
                     "http://localhost:5173", 
                     "http://localhost:5174", 
                     "http://127.0.0.1:5173",
                     "http://127.0.0.1:5174"
                 ],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "expose_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True
             }
         })
    

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    

    db.init_app(app)
    config_class.init_app(app)
    
    from .middleware import register_error_handlers
    register_error_handlers(app)
    

    from .routes.auth import auth_bp
    from .routes.music import music_bp
    from .routes.preferences import preferences_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(music_bp, url_prefix='/api/music')
    app.register_blueprint(preferences_bp, url_prefix='/api/preferences')
    

    from .models.user import User
    from .models.music import Music
    from .models.user_preference import UserPreference
    

    with app.app_context():
        print("Checking database tables (safe - only creates missing tables)...")
        db.create_all()
        print("Database tables ready!")
        
        from .services.ai_service import AIService
        ai_service = AIService()
        ai_service.initialize_model()
    
    return app 