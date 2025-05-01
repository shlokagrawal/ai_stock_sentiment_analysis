#app/models/sentiment.py

from app.models.db import db
from datetime import datetime

class SentimentData(db.Model):
    __tablename__ = 'sentiment_data'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    stock_symbol = db.Column(db.String(20), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    sentiment_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, stock_symbol, sentiment_score, source, text, stock_id=None):
        self.stock_symbol = stock_symbol
        self.sentiment_score = sentiment_score
        self.source = source
        self.text = text
        self.stock_id = stock_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'stock_symbol': self.stock_symbol,
            'source': self.source,
            'text': self.text,
            'sentiment_score': self.sentiment_score,
            'created_at': self.created_at.isoformat()
        } 