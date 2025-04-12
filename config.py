import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
if os.environ.get('DATABASE_URL'):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///thumbnails.db'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
