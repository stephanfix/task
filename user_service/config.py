# user_service/config.py
import os
from pathlib import Path

class Config:
    """Base configuration class"""
    
    # Flask Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database Settings
    DATABASE_PATH = os.getenv('DATABASE', './data/users.db')
    
    # Server Settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5001))
    
    # CORS Settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    @staticmethod
    def init_app(app):
        """Initialize application with this config"""
        # Create data directory if it doesn't exist
        db_dir = Path(Config.DATABASE_PATH).parent
        db_dir.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    # In production, these should come from environment variables only
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Ensure SECRET_KEY is set in production
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production!")


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    DATABASE_PATH = ':memory:'  # Use in-memory database for tests


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


# def get_config(env=None):
#     """Get configuration based on environment"""
#     if env is None:
#         env = os.getenv('FLASK_ENV', 'development')
#     return config.get(env, config['default'])

def get_config(env=None):
    if env == 'production':
        return ProductionConfig()
    return DevelopmentConfig()