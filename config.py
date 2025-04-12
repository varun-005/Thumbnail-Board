import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///thumbnails.db'
else:
    # Handle Render's Postgres URL format
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret key configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'development-key')
