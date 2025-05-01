import unittest
import sys
import os
from unittest.mock import patch

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.db import db
from app.models.stock import Stock
from app.models.recommendation import Recommendation
from app.models.user import User
from app.utils.auth import generate_token
import json
from datetime import datetime, timedelta

class TestRecommendationRoutes(unittest.TestCase):
    @patch('app.services.sentiment_service.scrape_news')
    @patch('app.services.sentiment_service.analyze_text')
    @patch('app.services.stock_service.get_historical_data')
    def setUp(self, mock_get_historical_data, mock_analyze_text, mock_scrape_news):
        """Set up test environment"""
        # Mock sentiment service functions
        mock_scrape_news.return_value = [
            {
                'compound_score': 0.8,
                'sentiment_label': 'positive',
                'published_at': datetime.utcnow().isoformat()
            }
        ]
        mock_analyze_text.return_value = {
            'compound_score': 0.8,
            'sentiment_label': 'positive'
        }
        
        # Mock stock service functions
        mock_get_historical_data.return_value = [
            {
                'date': (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'close': 150.0
            },
            {
                'date': datetime.utcnow().strftime('%Y-%m-%d'),
                'close': 160.0
            }
        ]

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
            password='testpass123'
        )
        db.session.add(self.test_user)
        db.session.commit()
        
        # Generate token for authentication
        self.token = generate_token(self.test_user.id)
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_stock_recommendation_by_symbol(self):
        """Test getting recommendation for a stock by symbol"""
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

        # Add a recommendation
        recommendation = Recommendation(
            stock_id=test_stock.id,
            analyst_id=self.test_user.id,
            type='buy',
            confidence_score=0.8,
            reason='Strong fundamentals and growth potential',
            price_target=160.0,
            time_frame='short-term'
        )
        db.session.add(recommendation)
        db.session.commit()

        response = self.client.get('/api/recommendations/stock/AAPL', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('stock', data)
        self.assertIn('recommendation', data)

    def test_get_top_recommendations(self):
        """Test getting top recommendations"""
        # First add stocks
        test_stock1 = Stock(
            symbol='AAPL',
            name='Apple Inc.',
            sector='Technology',
            current_price=150.0,
            previous_close=149.0
        )
        test_stock2 = Stock(
            symbol='MSFT',
            name='Microsoft Corp.',
            sector='Technology',
            current_price=300.0,
            previous_close=299.0
        )
        db.session.add_all([test_stock1, test_stock2])
        db.session.commit()

        # Add recommendations
        recommendation1 = Recommendation(
            stock_id=test_stock1.id,
            analyst_id=self.test_user.id,
            type='buy',
            confidence_score=0.8,
            reason='Strong fundamentals',
            price_target=160.0,
            time_frame='short-term'
        )
        recommendation2 = Recommendation(
            stock_id=test_stock2.id,
            analyst_id=self.test_user.id,
            type='hold',
            confidence_score=0.6,
            reason='Market uncertainty',
            price_target=310.0,
            time_frame='short-term'
        )
        db.session.add_all([recommendation1, recommendation2])
        db.session.commit()

        response = self.client.get('/api/recommendations/top', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('top_recommendations', data)

    def test_get_recommendation_history(self):
        """Test getting recommendation history for a stock"""
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

        # Add multiple recommendations
        recommendations = []
        for i in range(3):
            recommendation = Recommendation(
                stock_id=test_stock.id,
                analyst_id=self.test_user.id,
                type='buy' if i % 2 == 0 else 'hold',
                confidence_score=0.8 - (i * 0.1),
                reason=f'Test reason {i}',
                price_target=150.0 + (i * 10),
                time_frame='short-term'
            )
            recommendations.append(recommendation)
        db.session.add_all(recommendations)
        db.session.commit()

        response = self.client.get(f'/api/recommendations/history/{test_stock.id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('recommendation_history', data)
        self.assertIn('stock', data)

    def test_compare_stock_recommendations(self):
        """Test comparing recommendations for multiple stocks"""
        # First add stocks
        test_stock1 = Stock(
            symbol='AAPL',
            name='Apple Inc.',
            sector='Technology',
            current_price=150.0,
            previous_close=149.0
        )
        test_stock2 = Stock(
            symbol='MSFT',
            name='Microsoft Corp.',
            sector='Technology',
            current_price=300.0,
            previous_close=299.0
        )
        db.session.add_all([test_stock1, test_stock2])
        db.session.commit()

        response = self.client.post('/api/recommendations/compare',
            json={'stock_ids': [test_stock1.id, test_stock2.id]},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('recommendations', data)

    def test_get_all_recommendations(self):
        """Test getting recent recommendations for all stocks"""
        # First add stocks
        test_stock1 = Stock(
            symbol='AAPL',
            name='Apple Inc.',
            sector='Technology',
            current_price=150.0,
            previous_close=149.0
        )
        test_stock2 = Stock(
            symbol='MSFT',
            name='Microsoft Corp.',
            sector='Technology',
            current_price=300.0,
            previous_close=299.0
        )
        db.session.add_all([test_stock1, test_stock2])
        db.session.commit()

        # Add recent recommendations
        recommendation1 = Recommendation(
            stock_id=test_stock1.id,
            analyst_id=self.test_user.id,
            type='buy',
            confidence_score=0.8,
            reason='Strong fundamentals',
            price_target=160.0,
            time_frame='short-term'
        )
        recommendation2 = Recommendation(
            stock_id=test_stock2.id,
            analyst_id=self.test_user.id,
            type='hold',
            confidence_score=0.6,
            reason='Market uncertainty',
            price_target=310.0,
            time_frame='short-term'
        )
        db.session.add_all([recommendation1, recommendation2])
        db.session.commit()

        response = self.client.get('/api/recommendations/', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('recommendations', data)

    def test_invalid_stock_symbol(self):
        """Test getting recommendation for non-existent stock symbol"""
        response = self.client.get('/api/recommendations/stock/INVALID', headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_invalid_stock_id(self):
        """Test getting recommendation history for non-existent stock ID"""
        response = self.client.get('/api/recommendations/history/999', headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_access(self):
        """Test unauthorized access to recommendation routes"""
        response = self.client.get('/api/recommendations/')
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main() 