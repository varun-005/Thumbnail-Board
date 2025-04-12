import os
from dotenv import load_dotenv

load_dotenv()

# Get the PostgreSQL URL from Render
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Convert postgres:// to postgresql:// if necessary
    SQLALCHEMY_DATABASE_URI = database_url.replace('postgres://', 'postgresql://')
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///thumbnails.db'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
