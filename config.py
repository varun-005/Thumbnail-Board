import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///thumbnails.db')
if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_TRACK_MODIFICATIONS = False
