from app.models.db import db
from datetime import datetime

class SentimentData(db.Model):
    __tablename__ = 'sentiment_data'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    source = db.Column(db.String(100), nullable=False)  # news, twitter, reddit, etc.
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    url = db.Column(db.String(255))
    compound_score = db.Column(db.Float, nullable=False)  # VADER compound score
    positive_score = db.Column(db.Float, nullable=False)
    neutral_score = db.Column(db.Float, nullable=False)
    negative_score = db.Column(db.Float, nullable=False)
    sentiment_label = db.Column(db.String(20), nullable=False)  # positive, neutral, negative
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'source': self.source,
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'compound_score': self.compound_score,
            'positive_score': self.positive_score,
            'neutral_score': self.neutral_score,
            'negative_score': self.negative_score,
            'sentiment_label': self.sentiment_label,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat()
        } 