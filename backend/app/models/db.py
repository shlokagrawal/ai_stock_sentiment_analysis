from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    Migrate(app, db)
    
    # Import models to ensure they're registered with SQLAlchemy
    from app.models.user import User
    from app.models.stock import Stock
    from app.models.sentiment import SentimentData
    from app.models.recommendation import Recommendation
    from app.models.notification import Notification
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all() 