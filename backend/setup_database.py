#backend/setup_database.py

import os
import sys
from datetime import datetime, timedelta
import random
import hashlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a direct connection for database initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}:{os.environ.get('DB_PASSWORD', '')}@{os.environ.get('DB_HOST', 'localhost')}/{os.environ.get('DB_NAME', 'stock_sentiment')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Simple password hashing function that works on all Python versions
def simple_hash_password(password):
    salt = "stock_sentiment_salt"  # In production, use a proper salt strategy
    salted = (password + salt).encode('utf-8')
    return hashlib.sha256(salted).hexdigest()

# Define models directly (simplified versions just for initialization)
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = simple_hash_password(password)

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

class SentimentData(db.Model):
    __tablename__ = 'sentiment_data'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(20), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    url = db.Column(db.String(255))
    compound_score = db.Column(db.Float, nullable=False)
    positive_score = db.Column(db.Float, nullable=False)
    neutral_score = db.Column(db.Float, nullable=False)
    negative_score = db.Column(db.Float, nullable=False)
    sentiment_label = db.Column(db.String(20), nullable=False)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    price_target = db.Column(db.Float)
    time_frame = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    reference_id = db.Column(db.Integer)
    reference_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def create_sample_data():
    """Create sample data for the application"""
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create sample users if none exist
        if User.query.count() == 0:
            print("Creating sample users...")
            
            # Admin user
            admin = User(
                username="admin",
                email="admin@example.com",
                role="admin",
                is_active=True
            )
            admin.password = "admin123"
            
            # Analyst user
            analyst = User(
                username="analyst",
                email="analyst@example.com",
                role="analyst",
                is_active=True
            )
            analyst.password = "analyst123"
            
            # Regular user
            user = User(
                username="user",
                email="user@example.com",
                role="user",
                is_active=True
            )
            user.password = "user123"
            
            db.session.add_all([admin, analyst, user])
            db.session.commit()
            
            print(f"Created {User.query.count()} users")
        
        # Create sample stocks if none exist
        if Stock.query.count() == 0:
            print("Creating sample stocks...")
            
            stocks_data = [
                {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "current_price": 175.50, "previous_close": 174.20},
                {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "current_price": 332.80, "previous_close": 330.15},
                {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "current_price": 140.25, "previous_close": 139.50},
                {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Cyclical", "current_price": 145.70, "previous_close": 144.80},
                {"symbol": "TSLA", "name": "Tesla, Inc.", "sector": "Consumer Cyclical", "current_price": 260.50, "previous_close": 255.20},
                {"symbol": "META", "name": "Meta Platforms, Inc.", "sector": "Technology", "current_price": 325.80, "previous_close": 320.45},
                {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "current_price": 415.20, "previous_close": 410.65},
                {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services", "current_price": 142.30, "previous_close": 141.75},
                {"symbol": "V", "name": "Visa Inc.", "sector": "Financial Services", "current_price": 238.45, "previous_close": 237.20},
                {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "current_price": 152.80, "previous_close": 151.90}
            ]
            
            for stock_data in stocks_data:
                stock = Stock(**stock_data)
                db.session.add(stock)
            
            db.session.commit()
            
            print(f"Created {Stock.query.count()} stocks")
        
        # Add stocks to user's watchlist
        user = User.query.filter_by(username="user").first()
        if user:
            # Check if user already has stocks in watchlist
            watchlist_count = db.session.query(user_stocks).filter_by(user_id=user.id).count()
            
            if watchlist_count == 0:
                print("Adding stocks to user's watchlist...")
                
                # Add some stocks to the watchlist
                stocks = Stock.query.limit(5).all()
                
                for stock in stocks:
                    stmt = user_stocks.insert().values(
                        user_id=user.id,
                        stock_id=stock.id
                    )
                    db.session.execute(stmt)
                
                db.session.commit()
                
                print(f"Added {len(stocks)} stocks to user's watchlist")
        
        # Create sample sentiment data if none exists
        if SentimentData.query.count() == 0:
            print("Creating sample sentiment data...")
            
            stocks = Stock.query.all()
            
            # Sentiment sources
            sources = ["Yahoo Finance", "Market Watch", "CNBC", "Bloomberg", "Reuters"]
            
            # Sentiment data for the past week
            now = datetime.utcnow()
            
            sentiment_records = []
            
            for stock in stocks:
                # Generate between 5-15 sentiment records per stock
                for _ in range(random.randint(5, 15)):
                    # Random date within the past week
                    days_ago = random.randint(0, 7)
                    published_at = now - timedelta(days=days_ago, hours=random.randint(0, 24))
                    
                    # Random sentiment scores (simplified from original)
                    compound_score = random.uniform(-0.5, 0.8)
                    
                    if compound_score >= 0.05:
                        sentiment_label = "positive"
                        positive_score = random.uniform(0.5, 0.9)
                        neutral_score = random.uniform(0.1, 0.4)
                        negative_score = random.uniform(0, 0.1)
                    elif compound_score <= -0.05:
                        sentiment_label = "negative"
                        positive_score = random.uniform(0, 0.3)
                        neutral_score = random.uniform(0.2, 0.5)
                        negative_score = random.uniform(0.5, 0.8)
                    else:
                        sentiment_label = "neutral"
                        positive_score = random.uniform(0.2, 0.4)
                        neutral_score = random.uniform(0.5, 0.7)
                        negative_score = random.uniform(0.1, 0.3)
                    
                    # Create a sentiment record
                    sentiment_record = SentimentData(
                        stock_id=stock.id,
                        source=random.choice(sources),
                        title=f"Sample news about {stock.name}",
                        content=f"This is sample sentiment data for {stock.symbol} with a {sentiment_label} sentiment.",
                        url=f"https://example.com/{stock.symbol.lower()}/news",
                        compound_score=compound_score,
                        positive_score=positive_score,
                        neutral_score=neutral_score,
                        negative_score=negative_score,
                        sentiment_label=sentiment_label,
                        published_at=published_at,
                        created_at=published_at
                    )
                    
                    sentiment_records.append(sentiment_record)
            
            db.session.add_all(sentiment_records)
            db.session.commit()
            
            print(f"Created {len(sentiment_records)} sentiment records")
        
        # Create sample recommendations
        if Recommendation.query.count() == 0:
            print("Creating sample recommendations...")
            
            recommendations = []
            
            for stock in Stock.query.all():
                # Create recommendations based on average sentiment
                sentiment_data = SentimentData.query.filter_by(stock_id=stock.id).all()
                
                if sentiment_data:
                    # Calculate average sentiment
                    avg_sentiment = sum(record.compound_score for record in sentiment_data) / len(sentiment_data)
                    
                    # Determine recommendation type based on sentiment
                    if avg_sentiment > 0.25:
                        rec_type = "buy"
                        confidence_score = min(0.9, 0.5 + avg_sentiment * 0.5)
                        reason = f"Strong positive sentiment ({avg_sentiment:.2f}) for {stock.symbol}."
                        price_target = stock.current_price * 1.1
                        time_frame = "short-term"
                    elif avg_sentiment < -0.25:
                        rec_type = "sell"
                        confidence_score = min(0.9, 0.5 + abs(avg_sentiment) * 0.5)
                        reason = f"Strong negative sentiment ({avg_sentiment:.2f}) for {stock.symbol}."
                        price_target = stock.current_price * 0.9
                        time_frame = "short-term"
                    else:
                        rec_type = "hold"
                        confidence_score = 0.5
                        reason = f"Neutral sentiment ({avg_sentiment:.2f}) for {stock.symbol}."
                        price_target = stock.current_price
                        time_frame = "medium-term"
                else:
                    # Default recommendation if no sentiment data
                    rec_type = "hold"
                    confidence_score = 0.5
                    reason = f"Insufficient sentiment data for {stock.symbol}."
                    price_target = None
                    time_frame = "short-term"
                
                recommendation = Recommendation(
                    stock_id=stock.id,
                    type=rec_type,
                    confidence_score=confidence_score,
                    reason=reason,
                    price_target=price_target,
                    time_frame=time_frame,
                    created_at=datetime.utcnow() - timedelta(hours=random.randint(0, 12))
                )
                
                recommendations.append(recommendation)
            
            db.session.add_all(recommendations)
            db.session.commit()
            
            print(f"Created {len(recommendations)} recommendations")
        
        # Create sample notifications
        if Notification.query.count() == 0:
            print("Creating sample notifications...")
            
            notifications = []
            
            for user in User.query.all():
                # Create 3-5 notifications per user
                for _ in range(random.randint(3, 5)):
                    stock = random.choice(Stock.query.all())
                    
                    notification_types = ["alert", "recommendation", "news"]
                    notification_type = random.choice(notification_types)
                    
                    if notification_type == "alert":
                        title = f"Price Alert: {stock.symbol}"
                        message = f"{stock.symbol} has moved significantly. Current price: ${stock.current_price:.2f}"
                    elif notification_type == "recommendation":
                        title = f"New Recommendation: {stock.symbol}"
                        message = f"We have a new {random.choice(['buy', 'sell', 'hold'])} recommendation for {stock.symbol}"
                    else:  # news
                        title = f"News Alert: {stock.symbol}"
                        message = f"New important news about {stock.name} that might affect its price"
                    
                    notification = Notification(
                        user_id=user.id,
                        title=title,
                        message=message,
                        type=notification_type,
                        is_read=random.choice([True, False]),
                        reference_id=stock.id,
                        reference_type="stock",
                        created_at=datetime.utcnow() - timedelta(hours=random.randint(0, 24))
                    )
                    
                    notifications.append(notification)
            
            db.session.add_all(notifications)
            db.session.commit()
            
            print(f"Created {len(notifications)} notifications")
        
        print("Database initialized with sample data!")

if __name__ == "__main__":
    create_sample_data() 