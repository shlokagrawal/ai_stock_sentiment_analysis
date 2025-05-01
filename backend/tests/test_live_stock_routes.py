import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.db import db
from app.models.stock import Stock
from app.models.user import User
from app.utils.auth import generate_token
import json

class TestLiveStockRoutes(unittest.TestCase):
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
            role='admin'
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

    def test_get_live_stock_data(self):
        """Test getting live stock data"""
        # First add a stock
        test_stock = Stock(
            symbol='AAPL',
            name='Apple Inc.',
            sector='Technology',
            current_price=150.0,
            previous_close=149.0
        )
        db.session.add(test_stock)
        db.session.commit()
        
        response = self.client.get('/api/live-stocks/details/AAPL', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('stock', data)
        self.assertEqual(data['stock']['symbol'], 'AAPL')

    def test_get_live_stock_data_not_found(self):
        """Test getting live data for non-existent stock"""
        response = self.client.get('/api/live-stocks/details/NONEXISTENT', headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_get_live_stock_data_unauthorized(self):
        """Test getting live stock data without authentication"""
        response = self.client.get('/api/live-stocks/details/AAPL')
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main() 