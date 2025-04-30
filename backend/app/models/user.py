
# app/models/user.py

from app.models.db import db
from datetime import datetime
import hashlib

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # user, analyst, admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    # Simple password hashing function
    @staticmethod
    def hash_password(password):
        salt = "stock_sentiment_salt"  # Same salt as in setup_database.py
        salted = (password + salt).encode('utf-8')
        return hashlib.sha256(salted).hexdigest()
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = self.hash_password(password)
    
    def verify_password(self, password):
        return self.password_hash == self.hash_password(password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        } 