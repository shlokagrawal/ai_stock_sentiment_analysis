import yfinance as yf
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def test_symbol(symbol):
    """Test fetching data for a given symbol and print results"""
    print(f"\nTesting symbol: {symbol}")
    try:
        # Get the ticker
        ticker = yf.Ticker(symbol)
        
        # Get basic info
        info = ticker.info
        print(f"Successfully retrieved info with {len(info.keys())} keys")
        
        # Get current price
        if 'currentPrice' in info:
            print(f"Current price: {info['currentPrice']}")
        elif 'regularMarketPrice' in info:
            print(f"Current price: {info['regularMarketPrice']}")
        else:
            print("Price information not found in info")
        
        # Get historical data
        hist = ticker.history(period="5d")
        if hist.empty:
            print(f"No historical data available for {symbol}")
        else:
            print(f"Historical data rows: {len(hist)}")
            print(f"Latest close: {hist['Close'].iloc[-1]}")
        
        return True
    except Exception as e:
        print(f"Error processing {symbol}: {str(e)}")
        return False

if __name__ == "__main__":
    # Test with common symbols
    symbols = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"]
    
    # If symbols are provided via command line, use those instead
    if len(sys.argv) > 1:
        symbols = sys.argv[1:]
    
    success_count = 0
    for symbol in symbols:
        result = test_symbol(symbol)
        if result:
            success_count += 1
    
    print(f"\nSummary: Successfully tested {success_count} out of {len(symbols)} symbols.") 