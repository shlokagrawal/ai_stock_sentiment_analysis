from flask import Blueprint, request, jsonify
from app.models.db import db
from app.models.stock import Stock
from app.models.recommendation import Recommendation
from app.models.user import User
from app.services.recommendation_service import generate_recommendation, get_top_recommendations
from app.utils.auth import token_required, admin_required, analyst_required
from datetime import datetime, timedelta

recommendation_bp = Blueprint('recommendations', __name__)

@recommendation_bp.route('/stock/<int:stock_id>', methods=['GET'])
@token_required
def get_stock_recommendation(current_user, stock_id):
    """Get recommendation for a specific stock"""
    # Verify stock exists
    stock = Stock.query.get_or_404(stock_id)
    
    # Check if recent recommendation exists in database
    days = request.args.get('days', default=7, type=int)
    from_date = datetime.utcnow() - timedelta(days=1)  # Only use recommendations from the last day
    
    recent_recommendation = Recommendation.query.filter_by(
        stock_id=stock_id
    ).filter(
        Recommendation.created_at >= from_date
    ).order_by(
        Recommendation.created_at.desc()
    ).first()
    
    if recent_recommendation:
        return jsonify({
            'stock': stock.to_dict(),
            'recommendation': recent_recommendation.to_dict(),
            'is_cached': True
        }), 200
    
    # Generate new recommendation
    recommendation_data = generate_recommendation(stock_id, days=days)
    
    if not recommendation_data:
        return jsonify({
            'error': 'Failed to generate recommendation'
        }), 500
    
    # Save recommendation to database
    new_recommendation = Recommendation(
        stock_id=stock_id,
        type=recommendation_data['type'],
        confidence_score=recommendation_data['confidence_score'],
        reason=recommendation_data['reason'],
        price_target=recommendation_data.get('price_target'),
        time_frame=recommendation_data.get('time_frame', 'short-term')
    )
    
    db.session.add(new_recommendation)
    db.session.commit()
    
    # Return recommendation
    return jsonify({
        'stock': stock.to_dict(),
        'recommendation': new_recommendation.to_dict(),
        'details': recommendation_data,
        'is_cached': False
    }), 200

@recommendation_bp.route('/top', methods=['GET'])
@token_required
def get_top_stock_recommendations(current_user):
    """Get top stock recommendations"""
    limit = request.args.get('limit', default=5, type=int)
    
    # Get top recommendations
    top_recommendations = get_top_recommendations(limit=limit, user_id=current_user.id)
    
    if not top_recommendations:
        return jsonify({
            'error': 'Failed to generate top recommendations'
        }), 500
    
    # Get stock details for each recommendation
    recommendations_with_stocks = []
    
    for rec in top_recommendations:
        stock = Stock.query.get(rec['stock_id'])
        if stock:
            recommendations_with_stocks.append({
                'stock': stock.to_dict(),
                'recommendation': rec
            })
    
    return jsonify({
        'top_recommendations': recommendations_with_stocks
    }), 200

@recommendation_bp.route('/history/<int:stock_id>', methods=['GET'])
@token_required
def get_recommendation_history(current_user, stock_id):
    """Get recommendation history for a stock"""
    # Verify stock exists
    stock = Stock.query.get_or_404(stock_id)
    
    # Get time range from query params
    days = request.args.get('days', default=30, type=int)
    
    # Get recommendation history
    from_date = datetime.utcnow() - timedelta(days=days)
    
    recommendation_history = Recommendation.query.filter_by(
        stock_id=stock_id
    ).filter(
        Recommendation.created_at >= from_date
    ).order_by(
        Recommendation.created_at.asc()
    ).all()
    
    return jsonify({
        'stock': stock.to_dict(),
        'recommendation_history': [rec.to_dict() for rec in recommendation_history],
        'data_points': len(recommendation_history)
    }), 200

@recommendation_bp.route('/compare', methods=['POST'])
@token_required
def compare_stock_recommendations(current_user):
    """Compare recommendations for multiple stocks"""
    data = request.get_json()
    
    if not data or 'stock_ids' not in data:
        return jsonify({'error': 'No stock IDs provided'}), 400
    
    stock_ids = data['stock_ids']
    days = data.get('days', 7)
    
    if not stock_ids or not isinstance(stock_ids, list):
        return jsonify({'error': 'Invalid stock IDs format'}), 400
    
    # Get recommendations for each stock
    recommendations = []
    
    for stock_id in stock_ids:
        # Verify stock exists
        stock = Stock.query.get(stock_id)
        if not stock:
            continue
        
        # Generate recommendation
        recommendation_data = generate_recommendation(stock_id, days=days)
        
        if recommendation_data:
            recommendations.append({
                'stock': stock.to_dict(),
                'recommendation': recommendation_data
            })
    
    if not recommendations:
        return jsonify({
            'error': 'Failed to generate recommendations for the specified stocks'
        }), 500
    
    # Sort by confidence score and recommendation type
    recommendations.sort(key=lambda x: (
        1 if x['recommendation']['type'] == 'buy' else 0,
        x['recommendation']['confidence_score']
    ), reverse=True)
    
    return jsonify({
        'recommendations': recommendations
    }), 200

@recommendation_bp.route('/', methods=['GET'])
@token_required
def get_all_recommendations(current_user):
    """Get recent recommendations for all stocks"""
    # Get time range from query params
    days = request.args.get('days', default=1, type=int)
    
    # Get recent recommendations
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Get latest recommendation for each stock
    stocks = Stock.query.all()
    
    recommendations = []
    
    for stock in stocks:
        recent_recommendation = Recommendation.query.filter_by(
            stock_id=stock.id
        ).filter(
            Recommendation.created_at >= from_date
        ).order_by(
            Recommendation.created_at.desc()
        ).first()
        
        if recent_recommendation:
            recommendations.append({
                'stock': stock.to_dict(),
                'recommendation': recent_recommendation.to_dict()
            })
    
    return jsonify({
        'recommendations': recommendations
    }), 200 