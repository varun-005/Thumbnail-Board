#!/usr/bin/env bash
set -o errexit

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Print environment for debugging (mask sensitive info)
echo "Database URL format check:"
python << END
import os
url = os.getenv('DATABASE_URL', '')
print(f"Has URL: {'postgres://' in url or 'postgresql://' in url}")
END

# Initialize database
python << END
from app import app, db
with app.app_context():
    db.create_all()
    print("Database initialized!")
END
