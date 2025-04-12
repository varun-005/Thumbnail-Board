from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    if 'users' not in inspector.get_table_names():
        db.create_all()
        print("Database initialized successfully!")
    else:
        print("Database already exists, skipping initialization")
