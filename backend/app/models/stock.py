#app/models/stock.py

from app.models.db import db
from datetime import datetime
from app.models.recommendation import Recommendation

# User-Stock association table for watchlist
user_stocks = db.Table('user_stocks',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('stock_id', db.Integer, db.ForeignKey('stocks.id'), primary_key=True),
    db.Column('added_at', db.DateTime, default=datetime.utcnow)
)

class Stock(db.Model):
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    sector = db.Column(db.String(100))
    current_price = db.Column(db.Float)
    previous_close = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sentiment_data = db.relationship('SentimentData', backref='stock', lazy=True)
    recommendations = db.relationship('Recommendation', backref='stock', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'sector': self.sector,
            'current_price': self.current_price,
            'previous_close': self.previous_close,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        } 