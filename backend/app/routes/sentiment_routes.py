from flask import Blueprint, request, jsonify
from app.models.db import db
from app.models.stock import Stock
from app.models.sentiment import SentimentData
from app.services.sentiment_service import analyze_text, scrape_news, aggregate_sentiment
from app.utils.auth import token_required, admin_required, analyst_required
from datetime import datetime, timedelta

sentiment_bp = Blueprint('sentiment', __name__)

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

@sentiment_bp.route('/stock/<int:stock_id>', methods=['GET'])
@token_required
def get_stock_sentiment(current_user, stock_id):
    """Get sentiment data for a specific stock"""
    # Verify stock exists
    stock = Stock.query.get_or_404(stock_id)
    
    # Get time range from query params
    days = request.args.get('days', default=7, type=int)
    
    # Get sentiment data from database
    from_date = datetime.utcnow() - timedelta(days=days)
    
    sentiment_records = SentimentData.query.filter_by(
        stock_id=stock_id
    ).filter(
        SentimentData.created_at >= from_date
    ).order_by(
        SentimentData.created_at.desc()
    ).all()
    
    # Return sentiment data
    return jsonify({
        'stock': stock.to_dict(),
        'sentiment_data': [record.to_dict() for record in sentiment_records],
        'data_points': len(sentiment_records)
    }), 200

@sentiment_bp.route('/stock/<int:stock_id>/aggregate', methods=['GET'])
@token_required
def get_aggregate_sentiment(current_user, stock_id):
    """Get aggregated sentiment data for a specific stock"""
    # Verify stock exists
    stock = Stock.query.get_or_404(stock_id)
    
    # Get time range from query params
    days = request.args.get('days', default=7, type=int)
    
    # Get sentiment data from database
    from_date = datetime.utcnow() - timedelta(days=days)
    
    sentiment_records = SentimentData.query.filter_by(
        stock_id=stock_id
    ).filter(
        SentimentData.created_at >= from_date
    ).all()
    
    if not sentiment_records:
        return jsonify({
            'error': 'No sentiment data available for this stock'
        }), 404
    
    # Convert to list of dictionaries for aggregation
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
    
    # Aggregate sentiment
    aggregated = aggregate_sentiment(sentiment_data)
    
    if not aggregated:
        return jsonify({
            'error': 'Failed to aggregate sentiment data'
        }), 500
    
    return jsonify({
        'stock': stock.to_dict(),
        'aggregated_sentiment': aggregated
    }), 200

@sentiment_bp.route('/stock/<int:stock_id>/refresh', methods=['POST'])
@token_required
def refresh_sentiment(current_user, stock_id):
    """Refresh sentiment data for a stock by scraping new data"""
    # Verify stock exists
    stock = Stock.query.get_or_404(stock_id)
    
    # Scrape news for sentiment analysis
    news_items = scrape_news(stock.symbol, limit=10)
    
    if not news_items:
        return jsonify({
            'error': 'No news items found for this stock'
        }), 404
    
    # Save sentiment data to database
    new_records = []
    
    for item in news_items:
        # Check if this news item already exists
        existing = SentimentData.query.filter_by(
            stock_id=stock_id,
            title=item['title'],
            url=item['url']
        ).first()
        
        if existing:
            continue
        
        # Create new sentiment record
        sentiment_record = SentimentData(
            stock_id=stock_id,
            source=item['source'],
            title=item['title'],
            url=item['url'],
            compound_score=item['compound_score'],
            positive_score=item['positive_score'],
            neutral_score=item['neutral_score'],
            negative_score=item['negative_score'],
            sentiment_label=item['sentiment_label'],
            published_at=datetime.fromisoformat(item['published_at']) if 'published_at' in item else None
        )
        
        db.session.add(sentiment_record)
        new_records.append(sentiment_record)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Added {len(new_records)} new sentiment records',
        'new_records': [record.to_dict() for record in new_records]
    }), 200

@sentiment_bp.route('/stock/<int:stock_id>/sources/<source>', methods=['GET'])
@token_required
def get_sentiment_by_source(current_user, stock_id, source):
    """Get sentiment data for a specific stock and source"""
    # Verify stock exists
    stock = Stock.query.get_or_404(stock_id)
    
    # Get time range from query params
    days = request.args.get('days', default=7, type=int)
    
    # Get sentiment data from database
    from_date = datetime.utcnow() - timedelta(days=days)
    
    sentiment_records = SentimentData.query.filter_by(
        stock_id=stock_id,
        source=source
    ).filter(
        SentimentData.created_at >= from_date
    ).order_by(
        SentimentData.created_at.desc()
    ).all()
    
    # Return sentiment data
    return jsonify({
        'stock': stock.to_dict(),
        'source': source,
        'sentiment_data': [record.to_dict() for record in sentiment_records],
        'data_points': len(sentiment_records)
    }), 200 