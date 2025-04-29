from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

from app.routes.auth_routes import auth_bp
from app.routes.stock_routes import stock_bp
from app.routes.sentiment_routes import sentiment_bp
from app.routes.recommendation_routes import recommendation_bp
from app.routes.live_stock_routes import live_stock_bp
from app.models.db import init_db

# Load environment variables
load_dotenv()

def create_app():
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
    app.register_blueprint(live_stock_bp, url_prefix='/api/live-stocks')
    
    @app.route('/')
    def home():
        return {'message': 'Welcome to Stock Sentiment Analysis API'}
    
    @app.route('/debug/routes')
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "endpoint": rule.endpoint,
                "methods": list(rule.methods),
                "path": str(rule)
            })
        return {"routes": routes}
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=os.environ.get('FLASK_DEBUG', True)) 