from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'  # Explicitly name the table
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # Increased length for hash
    boards = db.relationship('Board', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Board(db.Model):
    __tablename__ = 'boards'  # Explicitly name the table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    thumbnails = db.relationship('Thumbnail', backref='board', lazy=True, cascade="all, delete-orphan")

class Thumbnail(db.Model):
    __tablename__ = 'thumbnails'  # Explicitly name the table
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(11), nullable=False)
    thumbnail_url = db.Column(db.String(255), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False)
