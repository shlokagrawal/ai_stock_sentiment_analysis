from datetime import datetime, timedelta

class StockCache:
    """Simple in-memory cache for stock data with time-to-live functionality"""
    _cache = {}  # symbol -> (data, timestamp)
    
    @classmethod
    def get(cls, symbol, max_age_minutes=15):
        """
        Get cached stock data if not expired
        
        Args:
            symbol (str): Stock symbol
            max_age_minutes (int): Maximum age of cached data in minutes
            
        Returns:
            dict or None: Cached stock data if valid, None otherwise
        """
        if symbol in cls._cache:
            data, timestamp = cls._cache[symbol]
            age = datetime.now() - timestamp
            if age < timedelta(minutes=max_age_minutes):
                return data
        return None
    
    @classmethod
    def set(cls, symbol, data):
        """
        Cache stock data with current timestamp
        
        Args:
            symbol (str): Stock symbol
            data (dict): Stock data to cache
        """
        cls._cache[symbol] = (data, datetime.now())
    
    @classmethod
    def clear(cls, symbol=None):
        """
        Clear cache for a specific symbol or all symbols
        
        Args:
            symbol (str, optional): Stock symbol to clear from cache. If None, clear all.
        """
        if symbol:
            if symbol in cls._cache:
                del cls._cache[symbol]
        else:
            cls._cache.clear() 