#!/usr/bin/env bash
set -o errexit

# Install Python dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
python << END
from app import app, db
with app.app_context():
    db.create_all()
    print("Database initialized successfully!")
END
