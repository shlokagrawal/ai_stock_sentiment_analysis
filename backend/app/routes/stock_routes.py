#app/routes/stock_routes.py


from flask import Blueprint, request, jsonify
from app.models.db import db
from app.models.stock import Stock, user_stocks
from app.models.user import User
from app.utils.auth import token_required, admin_required
from app.services.stock_service import fetch_stock_data
from app.utils.cache import StockCache

stock_bp = Blueprint('stocks', __name__)

@stock_bp.route('/', methods=['GET'])
@token_required
def get_stocks(current_user):
    """Get all stocks or filter by sector or symbol"""
    sector = request.args.get('sector')
    symbol = request.args.get('symbol')
    
    query = Stock.query
    
    if sector:
        query = query.filter_by(sector=sector)
    
    if symbol:
        query = query.filter(Stock.symbol.ilike(f'%{symbol}%'))
    
    stocks = query.all()
    
    return jsonify({
        'stocks': [stock.to_dict() for stock in stocks]
    }), 200

@stock_bp.route('/<string:symbol>', methods=['GET'])
@token_required
def get_stock_by_symbol(current_user, symbol):
    """Get a specific stock by symbol"""
    stock = Stock.query.filter_by(symbol=symbol.upper()).first()
    
    if not stock:
        return jsonify({'error': 'Stock not found'}), 404
    
    return jsonify({
        'stock': stock.to_dict()
    }), 200

@stock_bp.route('/<int:stock_id>', methods=['GET'])
def get_stock(stock_id):
    """Get a specific stock by ID"""
    stock = Stock.query.get_or_404(stock_id)
    
    return jsonify({
        'stock': stock.to_dict()
    }), 200

@stock_bp.route('/', methods=['POST'])
@token_required
@admin_required
def add_stock(current_user):
    """Add a new stock (admin only)"""
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ('symbol', 'name')):
        return jsonify({'error': 'Symbol and name are required'}), 400
    
    # Check if stock already exists
    existing_stock = Stock.query.filter_by(symbol=data['symbol']).first()
    if existing_stock:
        return jsonify({'error': 'Stock with this symbol already exists'}), 409
    
    # Create new stock
    new_stock = Stock(
        symbol=data['symbol'].upper(),
        name=data['name'],
        sector=data.get('sector')
    )
    
    # Try to fetch current price data
    try:
        stock_data = fetch_stock_data(data['symbol'])
        if stock_data:
            new_stock.current_price = stock_data.get('current_price')
            new_stock.previous_close = stock_data.get('previous_close')
    except Exception as e:
        # Just log the error but continue with creation
        print(f"Error fetching stock data: {str(e)}")
    
    db.session.add(new_stock)
    db.session.commit()
    
    return jsonify({
        'message': 'Stock added successfully',
        'stock': new_stock.to_dict()
    }), 201

@stock_bp.route('/<int:stock_id>', methods=['PUT'])
@token_required
@admin_required
def update_stock(current_user, stock_id):
    """Update a stock (admin only)"""
    stock = Stock.query.get_or_404(stock_id)
    data = request.get_json()
    
    # Update fields if provided
    if 'name' in data:
        stock.name = data['name']
    
    if 'sector' in data:
        stock.sector = data['sector']
    
    if 'current_price' in data:
        stock.current_price = data['current_price']
    
    if 'previous_close' in data:
        stock.previous_close = data['previous_close']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Stock updated successfully',
        'stock': stock.to_dict()
    }), 200

@stock_bp.route('/<int:stock_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_stock(current_user, stock_id):
    """Delete a stock (admin only)"""
    stock = Stock.query.get_or_404(stock_id)
    
    db.session.delete(stock)
    db.session.commit()
    
    return jsonify({
        'message': 'Stock deleted successfully'
    }), 200

@stock_bp.route('/refresh/<int:stock_id>', methods=['POST'])
@token_required
def refresh_stock_data(current_user, stock_id):
    """Refresh stock data from API"""
    stock = Stock.query.get_or_404(stock_id)
    
    try:
        stock_data = fetch_stock_data(stock.symbol)
        if stock_data:
            stock.current_price = stock_data.get('current_price')
            stock.previous_close = stock_data.get('previous_close')
            stock.last_updated = db.func.now()
            db.session.commit()
            
            return jsonify({
                'message': 'Stock data refreshed successfully',
                'stock': stock.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Failed to fetch stock data'}), 400
    except Exception as e:
        return jsonify({'error': f'Error refreshing stock data: {str(e)}'}), 500

# User watchlist routes
@stock_bp.route('/watchlist', methods=['GET'])
@token_required
def get_watchlist(current_user):
    """Get current user's watchlist"""
    user = User.query.get(current_user.id)
    watchlist_stocks = db.session.query(Stock).join(
        user_stocks, Stock.id == user_stocks.c.stock_id
    ).filter(
        user_stocks.c.user_id == user.id
    ).all()
    
    return jsonify({
        'watchlist': [stock.to_dict() for stock in watchlist_stocks]
    }), 200

@stock_bp.route('/watchlist/<int:stock_id>', methods=['POST'])
@token_required
def add_to_watchlist(current_user, stock_id):
    """Add stock to user's watchlist"""
    # Check if stock exists
    stock = Stock.query.get_or_404(stock_id)
    
    # Check if already in watchlist
    is_in_watchlist = db.session.query(user_stocks).filter_by(
        user_id=current_user.id, stock_id=stock_id
    ).first() is not None
    
    if is_in_watchlist:
        return jsonify({'error': 'Stock already in watchlist'}), 409
    
    # Add to watchlist
    stmt = user_stocks.insert().values(
        user_id=current_user.id,
        stock_id=stock_id
    )
    db.session.execute(stmt)
    db.session.commit()
    
    return jsonify({
        'message': 'Stock added to watchlist successfully'
    }), 201

@stock_bp.route('/watchlist/<int:stock_id>', methods=['DELETE'])
@token_required
def remove_from_watchlist(current_user, stock_id):
    """Remove stock from user's watchlist"""
    # Check if stock exists
    Stock.query.get_or_404(stock_id)
    
    # Remove from watchlist
    stmt = user_stocks.delete().where(
        user_stocks.c.user_id == current_user.id,
        user_stocks.c.stock_id == stock_id
    )
    result = db.session.execute(stmt)
    db.session.commit()
    
    if result.rowcount == 0:
        return jsonify({'error': 'Stock not in watchlist'}), 404
    
    return jsonify({
        'message': 'Stock removed from watchlist successfully'
    }), 200

@stock_bp.route('/search', methods=['POST'])
@token_required
def search_stock(current_user):
    """
    Search for a stock by symbol and analyze it (create if not exists)
    Uses Yahoo Finance API and caching to avoid excessive API calls
    """
    data = request.get_json()
    
    if not data or 'symbol' not in data:
        return jsonify({'error': 'No symbol provided'}), 400
    
    symbol = data['symbol'].upper()
    
    # Try to get from cache first (fast)
    cached_stock = StockCache.get(symbol)
    if cached_stock:
        return jsonify({
            'stock': cached_stock,
            'source': 'cache'
        }), 200
    
    # Next, try to find the stock in our database
    stock = Stock.query.filter_by(symbol=symbol).first()
    
    if stock:
        # Cache the stock data for future requests
        stock_dict = stock.to_dict()
        StockCache.set(symbol, stock_dict)
        return jsonify({
            'stock': stock_dict,
            'source': 'database'
        }), 200
    
    # If not found in cache or database, try to fetch from Yahoo Finance
    try:
        stock_data = fetch_stock_data(symbol)
        if not stock_data:
            return jsonify({'error': 'Stock not found'}), 404
            
        # Create new stock entry
        new_stock = Stock(
            symbol=symbol,
            name=stock_data.get('name', ''),
            sector=stock_data.get('sector', ''),
            current_price=stock_data.get('current_price'),
            previous_close=stock_data.get('previous_close')
        )
        
        db.session.add(new_stock)
        db.session.commit()
        
        # Cache the new stock data
        stock_dict = new_stock.to_dict()
        StockCache.set(symbol, stock_dict)
        
        return jsonify({
            'stock': stock_dict,
            'source': 'api'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 