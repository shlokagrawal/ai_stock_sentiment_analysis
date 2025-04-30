# app/routes/live_stock_routes.py

from flask import Blueprint, request, jsonify
from app.utils.auth import token_required
import yfinance as yf
from app.models.db import db

import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create a blueprint for live stock routes
live_stock_bp = Blueprint('live_stocks', __name__)

def fetch_stock_from_internet(symbol):
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        if 'shortName' not in info:
            return None  # Stock not found or invalid
        
        return {
            'symbol': symbol.upper(),
            'name': info.get('shortName', 'N/A'),
            'current_price': info.get('regularMarketPrice', None),
            'previous_close': info.get('previousClose', None),
            'market_cap': info.get('marketCap', None),
            'volume': info.get('volume', None),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'country': info.get('country', 'N/A'),
            'pe_ratio': info.get('trailingPE', None),
            'dividend_yield': info.get('dividendYield', None),
            'website': info.get('website', None),
        }
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        return None

@live_stock_bp.route('/search', methods=['POST'])
@token_required
def search_live_stock(current_user):
    """
    Search for a stock by symbol from the internet, and ensure it's stored in DB with sentiment.
    """
    data = request.get_json()

    if not data or 'symbol' not in data:
        return jsonify({'error': 'No symbol provided'}), 400

    symbol = data['symbol'].upper()
    logger.info(f"Searching for stock: {symbol}")

    stock_data = fetch_stock_from_internet(symbol)

    if not stock_data:
        return jsonify({'error': f'Could not find stock with symbol {symbol}'}), 404

    # ✅ Step 1: Add stock to DB if not exists
    from app.models.stock import Stock
    stock = Stock.query.filter_by(symbol=symbol).first()
    if not stock:
        stock = Stock(
    symbol=symbol,
    name=stock_data['name'],
    current_price=stock_data.get('current_price'),
    previous_close=stock_data.get('previous_close'),
    sector=stock_data.get('sector')
)
        db.session.add(stock)
        db.session.commit()

    # ✅ Step 2: Trigger sentiment scraping (with save_to_db=True)
    from app.services.sentiment_service import scrape_news
    scrape_news(symbol, limit=5, save_to_db=True)

    return jsonify({
        'stock': stock_data,
        'source': 'internet_and_cached'
    }), 200

@live_stock_bp.route('/details/<string:symbol>', methods=['GET'])
@token_required
def get_live_stock_details(current_user, symbol):
    """
    Get detailed stock information from internet
    """
    symbol = symbol.upper()

    stock_data = fetch_stock_from_internet(symbol)

    if not stock_data:
        return jsonify({'error': f'Could not find stock with symbol {symbol}'}), 404

    return jsonify({
        'stock': stock_data,
        'source': 'internet'
    }), 200

@live_stock_bp.route('/history/<string:symbol>', methods=['GET'])
@token_required
def get_live_stock_history(current_user, symbol):
    """
    Get historical data for a stock from internet
    """
    symbol = symbol.upper()

    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period='1mo')  # Default 1 month history

        history = []
        for date, row in hist.iterrows():
            history.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': int(row['Volume']),
            })

        return jsonify({
            'symbol': symbol,
            'period': '1mo',
            'history': history,
            'message': 'Fetched historical data from Yahoo Finance',
            'source': 'internet'
        }), 200
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        return jsonify({'error': f'Could not fetch historical data for {symbol}'}), 500
