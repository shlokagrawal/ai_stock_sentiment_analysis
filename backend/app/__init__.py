# This file is intentionally left empty to make the directory a Python package

from flask import Flask
from flask_cors import CORS
from .models.db import db
from .routes.auth_routes import auth_bp
from .routes.stock_routes import stock_bp
from .routes.sentiment_routes import sentiment_bp
from .routes.live_stock_routes import live_stock_bp
from .routes.recommendation_routes import recommendation_bp
from .config import config

def create_app(config_name='default'):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(stock_bp, url_prefix='/api/stocks')
    app.register_blueprint(sentiment_bp, url_prefix='/api/sentiment')
    app.register_blueprint(live_stock_bp, url_prefix='/api/live-stocks')
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommendations')
    
    return app
