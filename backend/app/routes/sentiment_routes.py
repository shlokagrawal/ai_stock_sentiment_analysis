# ✅ FILE: app/routes/sentiment_routes.py

from flask import Blueprint, request, jsonify
from app.models.db import db
from app.models.sentiment import SentimentData
from app.models.stock import Stock
from app.services.sentiment_service import analyze_text, scrape_news, aggregate_sentiment
from app.utils.auth import token_required
from datetime import datetime, timedelta

sentiment_bp = Blueprint('sentiment', __name__, url_prefix='/api/sentiment')

@sentiment_bp.route('/', methods=['POST'])
@token_required
def add_sentiment(current_user):
    """Add sentiment data for a stock"""
    data = request.get_json()
    
    if not all(k in data for k in ('stock_symbol', 'sentiment_score', 'source', 'text')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get or create stock
    stock = Stock.query.filter_by(symbol=data['stock_symbol']).first()
    if not stock:
        return jsonify({'error': 'Stock not found'}), 404
    
    # Create sentiment data
    sentiment = SentimentData(
        stock_symbol=data['stock_symbol'],
        sentiment_score=data['sentiment_score'],
        source=data['source'],
        text=data['text'],
        stock_id=stock.id
    )
    
    db.session.add(sentiment)
    db.session.commit()
    
    return jsonify({
        'message': 'Sentiment data added successfully',
        'sentiment': sentiment.to_dict()
    }), 201

@sentiment_bp.route('/analyze', methods=['POST'])
@token_required
def analyze_sentiment(current_user):
    """Analyze sentiment of provided text"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text']
    sentiment = analyze_text(text)
    
    if not sentiment:
        return jsonify({'error': 'Failed to analyze sentiment'}), 500
    
    return jsonify({
        'text': text,
        'sentiment': sentiment
    }), 200

@sentiment_bp.route('/stock/<string:symbol>', methods=['GET'])
@token_required
def get_stock_sentiment(current_user, symbol):
    """Get sentiment data for a specific stock symbol"""
    symbol = symbol.upper()
    days = request.args.get('days', default=7, type=int)
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Check if stock exists
    stock = Stock.query.filter_by(symbol=symbol).first()
    if not stock:
        return jsonify({'error': 'Stock not found'}), 404
    
    sentiment_records = SentimentData.query.filter_by(
        stock_symbol=symbol
    ).filter(
        SentimentData.created_at >= from_date
    ).order_by(
        SentimentData.created_at.desc()
    ).all()
    
    return jsonify({
        'symbol': symbol,
        'sentiment_data': [record.to_dict() for record in sentiment_records],
        'data_points': len(sentiment_records)
    }), 200

@sentiment_bp.route('/stock/<string:symbol>/aggregate', methods=['GET'])
@token_required
def get_aggregate_sentiment(current_user, symbol):
    """Get aggregated sentiment data for a specific stock symbol"""
    symbol = symbol.upper()
    days = request.args.get('days', default=7, type=int)
    from_date = datetime.utcnow() - timedelta(days=days)
    
    sentiment_records = SentimentData.query.filter_by(
        stock_symbol=symbol
    ).filter(
        SentimentData.created_at >= from_date
    ).all()
    
    if not sentiment_records:
        return jsonify({'error': 'No sentiment data available for this stock'}), 404
    
    sentiment_data = [
        {
            'compound_score': record.compound_score,
            'positive_score': record.positive_score,
            'neutral_score': record.neutral_score,
            'negative_score': record.negative_score,
            'sentiment_label': record.sentiment_label,
            'published_at': record.published_at.isoformat() if record.published_at else None,
            'source': record.source
        }
        for record in sentiment_records
    ]
    
    aggregated = aggregate_sentiment(sentiment_data)
    
    if not aggregated:
        return jsonify({'error': 'Failed to aggregate sentiment data'}), 500
    
    return jsonify({
        'symbol': symbol,
        'aggregated_sentiment': aggregated
    }), 200

@sentiment_bp.route('/stock/<string:symbol>/refresh', methods=['POST'])
@token_required
def refresh_sentiment(current_user, symbol):
    """Refresh sentiment data for a stock by scraping new data"""
    symbol = symbol.upper()
    
    # 🆕 Now scrape news and auto-save to DB
    news_items = scrape_news(symbol, limit=10, save_to_db=True)
    
    if not news_items:
        return jsonify({'error': 'No news items found for this stock'}), 404
    
    return jsonify({
        'message': f'Successfully refreshed sentiment for {symbol}.',
        'new_items': len(news_items)
    }), 200

@sentiment_bp.route('/stock/<string:symbol>/live', methods=['GET'])
@token_required
def get_live_sentiment(current_user, symbol):
    """Fetch live sentiment analysis from web scraper without touching database"""
    symbol = symbol.upper()
    
    # 🆕 Fetch latest news but DO NOT save to DB
    news_items = scrape_news(symbol, limit=5, save_to_db=False)
    
    if not news_items:
        return jsonify({'error': f'No live news found for {symbol}'}), 404
    
    return jsonify({
        'symbol': symbol,
        'live_sentiment': news_items,
        'count': len(news_items),
        'source': 'web_scraper'
    }), 200

@sentiment_bp.route('/stock/<string:symbol>/sources/<source>', methods=['GET'])
@token_required
def get_sentiment_by_source(current_user, symbol, source):
    """Get sentiment data for a specific stock symbol from a specific source"""
    symbol = symbol.upper()
    days = request.args.get('days', default=7, type=int)
    from_date = datetime.utcnow() - timedelta(days=days)
    
    sentiment_records = SentimentData.query.filter_by(
        stock_symbol=symbol,
        source=source
    ).filter(
        SentimentData.created_at >= from_date
    ).order_by(
        SentimentData.created_at.desc()
    ).all()
    
    return jsonify({
        'symbol': symbol,
        'source': source,
        'sentiment_data': [record.to_dict() for record in sentiment_records],
        'data_points': len(sentiment_records)
    }), 200
