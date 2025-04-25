import os
import sys
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database and model components directly
from app.models.db import db, init_db
from app.models.user import User
from app.models.stock import Stock, user_stocks
from app.models.sentiment import SentimentData
from app.models.recommendation import Recommendation
from app.models.notification import Notification
from app.routes.auth_routes import auth_bp
from app.routes.stock_routes import stock_bp
from app.routes.sentiment_routes import sentiment_bp
from app.routes.recommendation_routes import recommendation_bp

def create_app_for_init():
    """Create a Flask app instance specifically for database initialization"""
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}:{os.environ.get('DB_PASSWORD', '')}@{os.environ.get('DB_HOST', 'localhost')}/{os.environ.get('DB_NAME', 'stock_sentiment')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Initialize database
    init_db(app)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(stock_bp, url_prefix='/api/stocks')
    app.register_blueprint(sentiment_bp, url_prefix='/api/sentiment')
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommendations')
    
    return app

def create_sample_data():
    """Create sample data for the application"""
    
    # Create a Flask app specifically for this initialization
    app = create_app_for_init()
    
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
                    
                    # Random sentiment scores
                    # For demonstration, we'll lean positive for some stocks, negative for others
                    if stock.symbol in ["AAPL", "MSFT", "GOOGL", "NVDA"]:
                        # Mostly positive sentiment for tech leaders
                        compound_score = random.uniform(0.1, 0.8)
                        positive_score = random.uniform(0.6, 0.9)
                        neutral_score = random.uniform(0.1, 0.3)
                        negative_score = random.uniform(0, 0.1)
                        sentiment_label = "positive"
                    elif stock.symbol in ["TSLA"]:
                        # Mixed sentiment
                        compound_score = random.uniform(-0.3, 0.5)
                        if compound_score >= 0.05:
                            sentiment_label = "positive"
                            positive_score = random.uniform(0.5, 0.7)
                            neutral_score = random.uniform(0.2, 0.4)
                            negative_score = random.uniform(0.1, 0.2)
                        elif compound_score <= -0.05:
                            sentiment_label = "negative"
                            positive_score = random.uniform(0.1, 0.3)
                            neutral_score = random.uniform(0.2, 0.4)
                            negative_score = random.uniform(0.5, 0.7)
                        else:
                            sentiment_label = "neutral"
                            positive_score = random.uniform(0.3, 0.4)
                            neutral_score = random.uniform(0.5, 0.7)
                            negative_score = random.uniform(0.1, 0.2)
                    else:
                        # Random sentiment for other stocks
                        compound_score = random.uniform(-0.5, 0.5)
                        if compound_score >= 0.05:
                            sentiment_label = "positive"
                            positive_score = random.uniform(0.5, 0.8)
                            neutral_score = random.uniform(0.1, 0.4)
                            negative_score = random.uniform(0, 0.1)
                        elif compound_score <= -0.05:
                            sentiment_label = "negative"
                            positive_score = random.uniform(0.1, 0.3)
                            neutral_score = random.uniform(0.1, 0.4)
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
        
        # Create sample recommendations if none exist
        if Recommendation.query.count() == 0:
            print("Creating sample recommendations...")
            
            stocks = Stock.query.all()
            
            recommendations = []
            
            for stock in stocks:
                # Create a recommendation for each stock
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
                
                # Create recommendation
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
        
        # Create sample notifications if none exist
        if Notification.query.count() == 0:
            print("Creating sample notifications...")
            
            users = User.query.all()
            stocks = Stock.query.all()
            
            notifications = []
            
            for user in users:
                # Create 3-5 notifications per user
                for _ in range(random.randint(3, 5)):
                    stock = random.choice(stocks)
                    
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
                    
                    # Create notification
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