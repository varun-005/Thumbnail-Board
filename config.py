import os
from dotenv import load_dotenv

load_dotenv()

# Get environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///thumbnails.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Database configuration
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret key configuration
SECRET_KEY = os.getenv('RENDER_SECRET_KEY', 'development-key')
