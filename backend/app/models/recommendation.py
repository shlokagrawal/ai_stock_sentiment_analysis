#app/models/recommendation.py
# app/models/recommendation.py

from app.models.db import db
from datetime import datetime

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    analyst_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # e.g., 'buy', 'sell', 'hold'
    confidence_score = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text)
    price_target = db.Column(db.Float)
    time_frame = db.Column(db.String(20), default='short-term')  # e.g., 'short-term', 'medium-term', 'long-term'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyst = db.relationship('User', backref='recommendations', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'analyst_id': self.analyst_id,
            'type': self.type,
            'confidence_score': self.confidence_score,
            'reason': self.reason,
            'price_target': self.price_target,
            'time_frame': self.time_frame,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 