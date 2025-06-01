

A Flask-based REST API for music recommendation system following MVC architecture pattern.



This application follows the **Model-View-Controller (MVC)** pattern with additional layers for better separation of concerns:



```
backend/
├── app/
│   ├── __init__.py              
│   ├── config.py                
│   ├── controllers/             
│   │   ├── __init__.py
│   │   ├── base_controller.py   
│   │   ├── user_controller.py   
│   │   ├── music_controller.py  
│   │   └── preference_controller.py 
│   ├── models/                  
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── music.py
│   │   └── user_preference.py
│   ├── routes/                  
│   │   ├── auth.py
│   │   ├── music.py
│   │   └── preferences.py
│   ├── services/                
│   │   ├── __init__.py
│   │   ├── base_service.py      
│   │   ├── user_service.py
│   │   ├── music_service.py
│   │   ├── preference_service.py
│   │   └── ai_service.py        
│   ├── schemas/                 
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── music_schema.py
│   │   └── preference_schema.py
│   ├── utils/                   
│   │   ├── __init__.py
│   │   ├── helpers.py           
│   │   └── decorators.py        
│   └── middleware/              
│       ├── __init__.py
│       └── error_handlers.py    
├── instance/                    
│   └── music_app.db            
├── scripts/                     
├── run.py                      
├── requirements.txt            
└── README.md                   
```




- **Models**: Database entities using SQLAlchemy ORM
- **Views**: Route handlers that delegate to controllers
- **Controllers**: Business logic layer that coordinates between services


- Encapsulates business logic and data access
- Provides reusable components across controllers
- Includes AI recommendation service integration


- Uses Marshmallow for request/response validation
- Ensures data integrity and type safety
- Provides clear error messages for invalid data


- Environment-based configuration (development, production, testing)
- Centralized configuration with proper defaults
- Easy to extend and modify


- Global error handlers for consistent error responses
- Standardized error response format
- Proper HTTP status codes


- JWT-based authentication
- Token validation decorators
- User session management



1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables** (optional):
   ```bash
   export FLASK_ENV=development
   export SECRET_KEY=your-secret-key
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```




- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/verify` - Verify JWT token


- `GET /api/music/random` - Get random songs
- `GET /api/music/search` - Search songs
- `GET /api/music/songs/<song_id>` - Get song details
- `GET /api/music/tags` - Get all genres/tags
- `GET /api/music/by-genre` - Get songs by genre
- `GET /api/music/daily-mix` - Get AI-powered daily mix
- `GET /api/music/ai-status` - Check AI model status


- `GET /api/preferences/check-cold-start` - Check if user needs setup
- `POST /api/preferences/add-preferences` - Add multiple preferences (cold start)
- `GET /api/preferences/get-preferences` - Get user preferences
- `POST /api/preferences/add-preference` - Add single preference
- `DELETE /api/preferences/remove-preference` - Remove preference
- `GET /api/preferences/favourites-playlist` - Get favourites playlist



The application supports multiple environments:

- **Development**: SQLite database, debug mode enabled
- **Production**: Environment-based database URL, debug disabled
- **Testing**: In-memory SQLite database

Configure via environment variables:
- `FLASK_ENV`: Environment name (development/production/testing)
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: Database connection string (production)



1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Testability**: Easy to unit test individual components
3. **Maintainability**: Clear structure makes code easy to understand and modify
4. **Scalability**: Easy to add new features and endpoints
5. **Reusability**: Services can be reused across different controllers
6. **Consistency**: Standardized error handling and response formats
7. **Type Safety**: Schema validation ensures data integrity



1. **Controllers**: Keep them thin, delegate to services
2. **Services**: Contain business logic, interact with models
3. **Models**: Define database structure and relationships
4. **Schemas**: Validate input/output data
5. **Routes**: Simple delegation to controllers
6. **Utils**: Reusable helper functions and decorators

This architecture provides a solid foundation for building scalable and maintainable Flask applications. 