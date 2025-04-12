from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import re
import os
import requests
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
db.init_app(app)

# Error handling for production
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

from models import Board, Thumbnail, User

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        print(f"Login attempt - Email: {email}, User found: {user is not None}")  # Debug log
        
        if not user:
            return render_template('login.html', error="Email not found")
            
        if not user.check_password(password):
            return render_template('login.html', error="Incorrect password")
        
        session['user_id'] = user.id
        return redirect(url_for('app_page'))
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error="Email already registered")
        
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Instead of logging in directly, redirect to login with a success message
        return render_template('login.html', success="Registration successful! Please login.")
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('app_page'))
    return render_template('landing.html')

@app.route('/app')
def app_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/api/boards', methods=['GET', 'POST'])
def handle_boards():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Automatically generate a unique board name
        existing_boards = Board.query.filter_by(user_id=session['user_id']).all()
        existing_names = {board.name for board in existing_boards}
        board_number = 1
        while f"Board {board_number}" in existing_names:
            board_number += 1
        board_name = f"Board {board_number}"

        board = Board(name=board_name, user_id=session['user_id'])
        db.session.add(board)
        db.session.commit()
        return jsonify({"message": "Board created", "id": board.id, "name": board.name}), 201

    boards = Board.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{"id": board.id, "name": board.name} for board in boards])

@app.route('/api/boards/<int:board_id>', methods=['DELETE', 'PUT'])
def handle_board(board_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found"}), 404

    if request.method == 'DELETE':
        # Delete all thumbnails associated with the board
        Thumbnail.query.filter_by(board_id=board_id).delete()
        db.session.delete(board)
        db.session.commit()
        return jsonify({"message": "Board deleted"}), 200
    
    elif request.method == 'PUT':
        data = request.get_json()
        new_name = data.get('name')
        if not new_name:
            return jsonify({"error": "Board name is required"}), 400
        
        board.name = new_name
        db.session.commit()
        return jsonify({"message": "Board updated", "id": board.id, "name": board.name}), 200

@app.route('/api/thumbnails/<int:board_id>', methods=['GET', 'POST'])
def handle_thumbnails(board_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    board = Board.query.get(board_id)
    if not board:
        return jsonify({"error": "Board not found"}), 404

    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url')
        video_id = extract_video_id(url)

        if not video_id:
            return jsonify({"error": "Invalid YouTube URL"}), 400

        # Try maxresdefault first, if not available, use default quality
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        response = requests.head(thumbnail_url)
        if response.status_code != 200:
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        thumbnail = Thumbnail(video_id=video_id, thumbnail_url=thumbnail_url, board_id=board.id)
        db.session.add(thumbnail)
        db.session.commit()

        return jsonify({"message": "Thumbnail added", "thumbnail_url": thumbnail_url}), 201

    thumbnails = Thumbnail.query.filter_by(board_id=board.id).all()
    return jsonify([
        {"id": t.id, "video_id": t.video_id, "thumbnail_url": t.thumbnail_url}
        for t in thumbnails
    ])

@app.route('/api/thumbnails/<int:thumbnail_id>', methods=['DELETE'])
def delete_thumbnail(thumbnail_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    thumbnail = Thumbnail.query.get(thumbnail_id)
    if not thumbnail:
        return jsonify({"error": "Thumbnail not found"}), 404

    db.session.delete(thumbnail)
    db.session.commit()
    return jsonify({"message": "Thumbnail deleted"}), 200

@app.route('/api/download_thumbnail/<int:thumbnail_id>')
def download_thumbnail(thumbnail_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    thumbnail = Thumbnail.query.get(thumbnail_id)
    if not thumbnail:
        return jsonify({"error": "Thumbnail not found"}), 404

    try:
        response = requests.get(thumbnail.thumbnail_url, stream=True)
        if response.status_code == 200:
            image = BytesIO(response.content)
            return send_file(
                image,
                mimetype='image/jpeg',  # Adjust mimetype if necessary
                as_attachment=True,
                download_name=f"thumbnail_{thumbnail_id}.jpg"
            )
        else:
            return jsonify({"error": "Failed to fetch thumbnail"}), 500
    except Exception as e:
        print(f"Error downloading thumbnail: {e}")
        return jsonify({"error": "Error downloading thumbnail"}), 500

def extract_video_id(url):
    # Handle various YouTube URL formats
    patterns = [
        r"(?:v=|/)([0-9A-Za-z_-]{11})",  # Standard YouTube URL
        r"youtu\.be/([0-9A-Za-z_-]{11})",  # Shortened YouTube URL
        r"youtube\.com/embed/([0-9A-Za-z_-]{11})"  # Embedded YouTube URL
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None  # Return None if no match is found

from sqlalchemy import inspect

def init_db():
    with app.app_context():
        inspector = inspect(db.engine)
        if 'users' not in inspector.get_table_names():
            db.create_all()
            print("Database initialized successfully!")
        else:
            print("Database already exists, skipping initialization")

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
