from flask import Blueprint, request, jsonify
from app.models.db import db
from app.models.stock import Stock
from app.utils.auth import token_required, admin_required
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create a blueprint for live stock routes
live_stock_bp = Blueprint('live_stocks', __name__)

@live_stock_bp.route('/search', methods=['POST'])
@token_required
def search_live_stock(current_user):
    """
    Search for a stock by symbol in the database
    """
    data = request.get_json()
    
    if not data or 'symbol' not in data:
        return jsonify({'error': 'No symbol provided'}), 400
    
    symbol = data['symbol'].upper()
    logger.info(f"Searching for stock: {symbol}")
    
    # Find the stock in the database
    stock = Stock.query.filter_by(symbol=symbol).first()
    
    if stock:
        logger.info(f"Found {symbol} in database")
        stock_dict = stock.to_dict()
        
        # Return the stock data
        return jsonify({
            'stock': stock_dict,
            'source': 'database'
        }), 200
    else:
        logger.error(f"Could not find stock with symbol {symbol}")
        return jsonify({'error': f'Could not find stock with symbol {symbol}'}), 404

@live_stock_bp.route('/details/<string:symbol>', methods=['GET'])
@token_required
def get_live_stock_details(current_user, symbol):
    """Get detailed stock information from database"""
    symbol = symbol.upper()
    
    # Find the stock in the database
    stock = Stock.query.filter_by(symbol=symbol).first()
    
    if not stock:
        return jsonify({'error': f'Could not find stock with symbol {symbol}'}), 404
    
    stock_dict = stock.to_dict()
    
    return jsonify({
        'stock': stock_dict,
        'source': 'database'
    }), 200

@live_stock_bp.route('/history/<string:symbol>', methods=['GET'])
@token_required
def get_live_stock_history(current_user, symbol):
    """Get historical data for a stock"""
    symbol = symbol.upper()
    
    # Find the stock in the database
    stock = Stock.query.filter_by(symbol=symbol).first()
    
    if not stock:
        return jsonify({'error': f'Could not find stock with symbol {symbol}'}), 404
    
    # For now, return a basic response since historical data will be handled differently
    return jsonify({
        'symbol': symbol,
        'period': '1mo',
        'history': [],
        'message': 'Historical data is not available without Yahoo Finance integration'
    }), 200 