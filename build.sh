#!/usr/bin/env bash
set -o errexit

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Print environment for debugging
echo "DATABASE_URL: $DATABASE_URL"

# Initialize database
python << END
from app import app, db
with app.app_context():
    db.create_all()
    print("Database initialized!")
END
