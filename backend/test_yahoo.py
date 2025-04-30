#backend/test_yahoo.py

import yfinance as yf
import sys

def test_yahoo_finance(symbol):
    print(f"Testing Yahoo Finance for symbol: {symbol}")
    try:
        # Get the ticker
        ticker = yf.Ticker(symbol)
        
        # Get basic info and recent data
        info = ticker.info
        hist = ticker.history(period="2d")
        
        if hist.empty:
            print(f"No historical data available for {symbol}")
            return None
        
        # Print some basic info
        print(f"Info keys: {list(info.keys())}")
        
        if 'regularMarketPrice' in info:
            print(f"Current price: {info['regularMarketPrice']}")
        elif 'currentPrice' in info:
            print(f"Current price: {info['currentPrice']}")
        else:
            print(f"Price not found in info, using history: {hist['Close'].iloc[-1]}")
        
        # Print some history
        print(f"History columns: {hist.columns}")
        print(f"History rows: {len(hist)}")
        if len(hist) > 0:
            print(f"Latest close: {hist['Close'].iloc[-1]}")
        
        return True
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None

if __name__ == "__main__":
    # Test with a few symbols
    symbols = ["AAPL", "MSFT", "GOOG", "SXT"]
    if len(sys.argv) > 1:
        symbols = sys.argv[1:]
    
    for symbol in symbols:
        print("\n" + "="*50)
        result = test_yahoo_finance(symbol)
        if result:
            print(f"Successfully fetched data for {symbol}")
        else:
            print(f"Failed to fetch data for {symbol}") 