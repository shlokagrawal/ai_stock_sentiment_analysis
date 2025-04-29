import requests
import json
import sys

def test_search_endpoint(symbol):
    """Test the live stock search endpoint"""
    url = "http://localhost:5000/api/live-stocks/search"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ENTER_VALID_TOKEN_HERE'  # Update with a valid token
    }
    data = {
        'symbol': symbol
    }
    
    print(f"Testing search endpoint with symbol: {symbol}")
    print(f"Request URL: {url}")
    print(f"Request data: {json.dumps(data)}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"Source: {result.get('source', 'unknown')}")
            if 'stock' in result:
                stock = result['stock']
                print(f"Stock name: {stock.get('name', 'unknown')}")
                print(f"Stock symbol: {stock.get('symbol', 'unknown')}")
                print(f"Current price: {stock.get('current_price', 'unknown')}")
            if 'message' in result:
                print(f"Message: {result['message']}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

if __name__ == "__main__":
    # Default symbol to test
    symbols = ["AAPL", "MSFT", "GOOG", "SXT"]
    
    if len(sys.argv) > 1:
        symbols = sys.argv[1:]
    
    for symbol in symbols:
        print("\n" + "="*50)
        test_search_endpoint(symbol) 