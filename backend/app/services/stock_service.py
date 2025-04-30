#app/services/stock_service.py

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import logging

logger = logging.getLogger(__name__)

def fetch_stock_data(symbol):
    """
    Fetch stock data from Yahoo Finance
    
    Args:
        symbol (str): Stock ticker symbol
        
    Returns:
        dict: Stock data including current price and previous close
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Get the basic information
        info = ticker.info
        
        # Get historical data for the past 2 days to ensure we have previous close
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)  # Get 5 days to ensure we have enough data even with weekends
        hist_data = ticker.history(start=start_date, end=end_date)
        
        # Handle empty data
        if hist_data.empty:
            logger.warning(f"No historical data available for {symbol}")
            return None
        
        # Get the latest data and previous close
        latest_data = hist_data.iloc[-1]
        
        # Get previous close (if available)
        previous_close = None
        if len(hist_data) > 1:
            previous_close = hist_data.iloc[-2]['Close']
        else:
            # Fallback to info's previous close if available
            previous_close = info.get('previousClose')
        
        # Prepare the response
        stock_data = {
            'symbol': symbol,
            'name': info.get('shortName', info.get('longName', symbol)),
            'current_price': latest_data['Close'],
            'previous_close': previous_close,
            'open': latest_data['Open'],
            'high': latest_data['High'],
            'low': latest_data['Low'],
            'volume': latest_data['Volume'],
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'dividend_yield': info.get('dividendYield'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'timestamp': datetime.now().isoformat()
        }
        
        return stock_data
        
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
        return None

def get_historical_data(symbol, period='1mo'):
    """
    Get historical stock data for a specific period
    
    Args:
        symbol (str): Stock ticker symbol
        period (str): Period of historical data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
    Returns:
        pd.DataFrame: Historical stock data
    """
    try:
        ticker = yf.Ticker(symbol)
        hist_data = ticker.history(period=period)
        
        # Convert DataFrame to a dictionary with date strings
        result = []
        for date, row in hist_data.iterrows():
            result.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': row['Volume']
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
        return None

def search_stocks(query):
    """
    Search for stocks based on a query
    
    Args:
        query (str): Search query (symbol or company name)
        
    Returns:
        list: List of matching stocks
    """
    # For simplicity, we'll use a predefined list of popular stocks
    # In a real-world scenario, you would use an API or database to search
    popular_stocks = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'sector': 'Technology'},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Technology'},
        {'symbol': 'AMZN', 'name': 'Amazon.com, Inc.', 'sector': 'Consumer Cyclical'},
        {'symbol': 'TSLA', 'name': 'Tesla, Inc.', 'sector': 'Consumer Cyclical'},
        {'symbol': 'META', 'name': 'Meta Platforms, Inc.', 'sector': 'Technology'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'sector': 'Technology'},
        {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.', 'sector': 'Financial Services'},
        {'symbol': 'V', 'name': 'Visa Inc.', 'sector': 'Financial Services'},
        {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'sector': 'Healthcare'}
    ]
    
    # Filter stocks based on the query
    query = query.lower()
    matching_stocks = [
        stock for stock in popular_stocks
        if query in stock['symbol'].lower() or query in stock['name'].lower()
    ]
    
    return matching_stocks 