import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.db import db
from app.models.stock import Stock
from app.models.sentiment import SentimentData
from app.models.user import User
from app.utils.auth import generate_token
import json
from datetime import datetime, timedelta

class TestBackend(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create test database
        db.create_all()
        
        # Create test user
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='admin'  # Make user admin to test admin routes
        )
        db.session.add(self.test_user)
        db.session.commit()
        
        # Generate token for authenticated requests
        self.token = generate_token(self.test_user.id)
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration(self):
        """Test user registration endpoint"""
        response = self.client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'User registered successfully')

    def test_user_login(self):
        """Test user login endpoint"""
        response = self.client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)

    def test_get_stocks(self):
        """Test getting all stocks"""
        # Add test stock
        test_stock = Stock(
            symbol='TEST',
            name='Test Stock',
            current_price=100.0,
            previous_close=99.0
        )
        db.session.add(test_stock)
        db.session.commit()
    
        response = self.client.get('/api/stocks/', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('stocks', data)
        self.assertEqual(len(data['stocks']), 1)
        self.assertEqual(data['stocks'][0]['symbol'], 'TEST')

    def test_get_stock_by_symbol(self):
        """Test getting stock by symbol"""
        # Add test stock
        test_stock = Stock(
            symbol='TEST',
            name='Test Stock',
            current_price=100.0,
            previous_close=99.0
        )
        db.session.add(test_stock)
        db.session.commit()
    
        response = self.client.get('/api/stocks/TEST', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('stock', data)
        self.assertEqual(data['stock']['symbol'], 'TEST')

    def test_add_sentiment(self):
        """Test adding sentiment data"""
        # Add test stock first
        test_stock = Stock(
            symbol='TEST',
            name='Test Stock',
            current_price=100.0,
            previous_close=99.0
        )
        db.session.add(test_stock)
        db.session.commit()
    
        response = self.client.post('/api/sentiment/', json={
            'stock_symbol': 'TEST',
            'sentiment_score': 0.8,
            'source': 'test_source',
            'text': 'Test sentiment text'
        }, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('sentiment', data)

    def test_get_sentiment(self):
        """Test getting sentiment data"""
        # Add test stock and sentiment
        test_stock = Stock(
            symbol='TEST',
            name='Test Stock',
            current_price=100.0,
            previous_close=99.0
        )
        db.session.add(test_stock)
        db.session.commit()
    
        test_sentiment = SentimentData(
            stock_symbol='TEST',
            sentiment_score=0.8,
            source='test_source',
            text='Test sentiment text',
            stock_id=test_stock.id
        )
        db.session.add(test_sentiment)
        db.session.commit()
    
        response = self.client.get('/api/sentiment/stock/TEST', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('sentiment_data', data)
        self.assertEqual(len(data['sentiment_data']), 1)
        self.assertEqual(data['sentiment_data'][0]['stock_symbol'], 'TEST')

    def test_unauthorized_access(self):
        """Test unauthorized access to protected routes"""
        response = self.client.get('/api/stocks/')
        self.assertEqual(response.status_code, 401)

    def test_invalid_token(self):
        """Test access with invalid token"""
        headers = {
            'Authorization': 'Bearer invalid_token',
            'Content-Type': 'application/json'
        }
        response = self.client.get('/api/stocks/', headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_stock_not_found(self):
        """Test getting non-existent stock"""
        response = self.client.get('/api/stocks/NONEXISTENT', headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_sentiment_not_found(self):
        """Test getting sentiment for non-existent stock"""
        response = self.client.get('/api/sentiment/stock/NONEXISTENT', headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_add_stock(self):
        """Test adding a new stock (admin only)"""
        response = self.client.post('/api/stocks/', json={
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'sector': 'Technology'
        }, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('stock', data)
        self.assertEqual(data['stock']['symbol'], 'AAPL')

    def test_add_duplicate_stock(self):
        """Test adding a duplicate stock"""
        # First add a stock
        self.client.post('/api/stocks/', json={
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'sector': 'Technology'
        }, headers=self.headers)
        
        # Try to add the same stock again
        response = self.client.post('/api/stocks/', json={
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'sector': 'Technology'
        }, headers=self.headers)
        self.assertEqual(response.status_code, 409)

    def test_update_stock(self):
        """Test updating a stock"""
        # First add a stock
        self.client.post('/api/stocks/', json={
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'sector': 'Technology'
        }, headers=self.headers)
        
        # Get the stock
        stock = Stock.query.filter_by(symbol='AAPL').first()
        
        # Update the stock
        response = self.client.put(f'/api/stocks/{stock.id}', json={
            'name': 'Apple Inc. Updated',
            'sector': 'Consumer Electronics'
        }, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['stock']['name'], 'Apple Inc. Updated')
        self.assertEqual(data['stock']['sector'], 'Consumer Electronics')

    def test_delete_stock(self):
        """Test deleting a stock"""
        # First add a stock
        self.client.post('/api/stocks/', json={
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'sector': 'Technology'
        }, headers=self.headers)
        
        # Get the stock
        stock = Stock.query.filter_by(symbol='AAPL').first()
        
        # Delete the stock
        response = self.client.delete(f'/api/stocks/{stock.id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        # Verify stock is deleted
        deleted_stock = Stock.query.filter_by(symbol='AAPL').first()
        self.assertIsNone(deleted_stock)

    def test_refresh_stock_data(self):
        """Test refreshing stock data"""
        # First add a stock
        self.client.post('/api/stocks/', json={
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'sector': 'Technology'
        }, headers=self.headers)
        
        # Get the stock
        stock = Stock.query.filter_by(symbol='AAPL').first()
        
        # Refresh stock data
        response = self.client.post(f'/api/stocks/refresh/{stock.id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('stock', data)

    def test_add_to_watchlist(self):
        """Test adding stock to watchlist"""
        # First add a stock
        self.client.post('/api/stocks/', json={
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'sector': 'Technology'
        }, headers=self.headers)
        
        # Get the stock
        stock = Stock.query.filter_by(symbol='AAPL').first()
        
        # Add to watchlist
        response = self.client.post(f'/api/stocks/watchlist/{stock.id}', headers=self.headers)
        self.assertEqual(response.status_code, 201)
        
        # Get watchlist
        response = self.client.get('/api/stocks/watchlist', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['watchlist']), 1)
        self.assertEqual(data['watchlist'][0]['symbol'], 'AAPL')

    def test_remove_from_watchlist(self):
        """Test removing stock from watchlist"""
        # First add a stock and add it to watchlist
        self.client.post('/api/stocks/', json={
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'sector': 'Technology'
        }, headers=self.headers)
        
        stock = Stock.query.filter_by(symbol='AAPL').first()
        self.client.post(f'/api/stocks/watchlist/{stock.id}', headers=self.headers)
        
        # Remove from watchlist
        response = self.client.delete(f'/api/stocks/watchlist/{stock.id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        # Verify watchlist is empty
        response = self.client.get('/api/stocks/watchlist', headers=self.headers)
        data = json.loads(response.data)
        self.assertEqual(len(data['watchlist']), 0)

    def test_search_stock(self):
        """Test searching for a stock"""
        response = self.client.post('/api/stocks/search', json={
            'symbol': 'AAPL'
        }, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('stock', data)
        self.assertEqual(data['stock']['symbol'], 'AAPL')

    def test_get_stocks_by_sector(self):
        """Test getting stocks filtered by sector"""
        # Add stocks in different sectors
        self.client.post('/api/stocks/', json={
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'sector': 'Technology'
        }, headers=self.headers)
        
        self.client.post('/api/stocks/', json={
            'symbol': 'MSFT',
            'name': 'Microsoft Corp.',
            'sector': 'Technology'
        }, headers=self.headers)
        
        self.client.post('/api/stocks/', json={
            'symbol': 'JPM',
            'name': 'JPMorgan Chase',
            'sector': 'Financial'
        }, headers=self.headers)
        
        # Get stocks by sector
        response = self.client.get('/api/stocks/?sector=Technology', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['stocks']), 2)
        self.assertTrue(all(stock['sector'] == 'Technology' for stock in data['stocks']))

    def test_get_stocks_by_symbol_search(self):
        """Test searching stocks by symbol"""
        # Add stocks
        self.client.post('/api/stocks/', json={
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'sector': 'Technology'
        }, headers=self.headers)
        
        self.client.post('/api/stocks/', json={
            'symbol': 'MSFT',
            'name': 'Microsoft Corp.',
            'sector': 'Technology'
        }, headers=self.headers)
        
        # Search by symbol
        response = self.client.get('/api/stocks/?symbol=AA', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['stocks']), 1)
        self.assertEqual(data['stocks'][0]['symbol'], 'AAPL')

if __name__ == '__main__':
    unittest.main() 