import os
from dotenv import load_dotenv

load_dotenv()

# Check for valid database URL format
db_url = os.getenv('DATABASE_URL', '')
if db_url and ('postgres://' in db_url or 'postgresql://' in db_url):
    # Convert postgres:// to postgresql:// if needed
    SQLALCHEMY_DATABASE_URI = db_url.replace('postgres://', 'postgresql://')
else:
    # Fallback to SQLite for development or if URL is invalid
    SQLALCHEMY_DATABASE_URI = 'sqlite:///thumbnails.db'
    print(f"Warning: Using SQLite. Current DATABASE_URL: {db_url}")

SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
