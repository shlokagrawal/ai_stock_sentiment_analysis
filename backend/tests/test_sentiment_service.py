import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.sentiment_service import analyze_text, scrape_news, aggregate_sentiment
from app.models.stock import Stock
from app.models.sentiment import SentimentData

class TestSentimentService(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Create a mock stock
        self.test_stock = Stock(
            symbol='AAPL',
            name='Apple Inc.',
            sector='Technology',
            current_price=150.0,
            previous_close=149.0
        )

    def test_analyze_text(self):
        """Test text sentiment analysis"""
        # Test positive sentiment
        result = analyze_text("This is a great product!")
        self.assertIsNotNone(result)
        self.assertGreater(result['compound_score'], 0)
        self.assertEqual(result['sentiment_label'], 'positive')
        
        # Test negative sentiment
        result = analyze_text("This is a terrible product!")
        self.assertIsNotNone(result)
        self.assertLess(result['compound_score'], 0)
        self.assertEqual(result['sentiment_label'], 'negative')
        
        # Test neutral sentiment
        result = analyze_text("This is a product.")
        self.assertIsNotNone(result)
        self.assertEqual(result['sentiment_label'], 'neutral')

    @patch('app.services.sentiment_service.requests.get')
    def test_scrape_news(self, mock_get):
        """Test news scraping and sentiment analysis"""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'news': [
                {
                    'title': 'Great news for Apple!',
                    'link': 'http://example.com/1',
                    'publisher': 'Test News',
                    'providerPublishTime': datetime.now().timestamp()
                },
                {
                    'title': 'Bad news for Apple',
                    'link': 'http://example.com/2',
                    'publisher': 'Test News',
                    'providerPublishTime': datetime.now().timestamp()
                }
            ]
        }
        mock_get.return_value = mock_response
        mock_response.raise_for_status = MagicMock()
        
        # Test news scraping
        result = scrape_news('AAPL', limit=2, save_to_db=False)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertIn('compound_score', result[0])
        self.assertIn('sentiment_label', result[0])

    def test_aggregate_sentiment(self):
        """Test sentiment aggregation"""
        # Create test sentiment data
        sentiment_data = [
            {
                'compound_score': 0.8,
                'positive_score': 0.9,
                'neutral_score': 0.1,
                'negative_score': 0.0,
                'sentiment_label': 'positive',
                'published_at': datetime.now().isoformat()
            },
            {
                'compound_score': -0.6,
                'positive_score': 0.1,
                'neutral_score': 0.3,
                'negative_score': 0.6,
                'sentiment_label': 'negative',
                'published_at': datetime.now().isoformat()
            }
        ]
        
        # Test aggregation
        result = aggregate_sentiment(sentiment_data)
        
        self.assertIsNotNone(result)
        self.assertIn('compound_score', result)
        self.assertIn('sentiment_label', result)
        self.assertIn('sentiment_counts', result)
        self.assertIn('sentiment_percentages', result)
        self.assertEqual(result['data_points'], 2)

if __name__ == '__main__':
    unittest.main() 