#app/services/recommendation_service.py

import pandas as pd
import numpy as np
from app.models.sentiment import SentimentData
from app.models.stock import Stock
from datetime import datetime, timedelta
import logging
from app.services.stock_service import fetch_stock_data, get_historical_data

logger = logging.getLogger(__name__)

def generate_recommendation(stock_id, days=7):
    """
    Generate investment recommendation based on sentiment analysis and stock performance
    """
    try:
        stock = Stock.query.get(stock_id)
        if not stock:
            logger.error(f"Stock with ID {stock_id} not found")
            return None
        
        # Get fresh sentiment data
        from app.services.sentiment_service import scrape_news, analyze_text
        news_items = scrape_news(stock.symbol, limit=10)

        if not news_items:
            logger.warning(f"No live news found for stock {stock.symbol}")
            return {
                'stock_id': stock_id,
                'type': 'hold',
                'confidence_score': 0.5,
                'reason': f"Insufficient live news for {stock.symbol}.",
                'time_frame': 'short-term'
            }
        
        sentiment_df = pd.DataFrame([
            {
                'compound_score': item['compound_score'],
                'sentiment_label': item['sentiment_label'],
                'published_at': item['published_at']
            }
            for item in news_items
        ])

        # Get historical price data
        historical_data = get_historical_data(stock.symbol, period='1mo')
        if not historical_data:
            logger.warning(f"No historical price data available for stock {stock.symbol}")
            return generate_sentiment_only_recommendation(stock, sentiment_df)
        
        price_df = pd.DataFrame(historical_data)
        price_df['date'] = pd.to_datetime(price_df['date'])
        price_df = price_df.sort_values('date')

        if len(price_df) >= 2:
            start_price = price_df.iloc[0]['close']
            end_price = price_df.iloc[-1]['close']
            price_change_pct = (end_price - start_price) / start_price * 100
        else:
            price_change_pct = 0

        # Analyze sentiment trend
        sentiment_df['published_at'] = pd.to_datetime(sentiment_df['published_at'])
        sentiment_df = sentiment_df.sort_values('published_at')

        if len(sentiment_df) >= 4:
            mid_idx = len(sentiment_df) // 2
            early_sentiment = sentiment_df.iloc[:mid_idx]['compound_score'].mean()
            recent_sentiment = sentiment_df.iloc[mid_idx:]['compound_score'].mean()
            sentiment_trend = recent_sentiment - early_sentiment
        else:
            early_sentiment = sentiment_df['compound_score'].mean()
            recent_sentiment = early_sentiment
            sentiment_trend = 0

        avg_sentiment = sentiment_df['compound_score'].mean()

        # Recommendation Logic
        recommendation_type = 'hold'
        confidence_score = 0.5
        reason = ""
        price_target = None
        time_frame = 'short-term'

        if avg_sentiment > 0.25 and sentiment_trend >= 0 and price_change_pct > 0:
            recommendation_type = 'buy'
            confidence_score = min(0.9, 0.5 + avg_sentiment * 0.5)
            reason = f"Positive sentiment ({avg_sentiment:.2f}) with upward price trend (+{price_change_pct:.2f}%)."
            price_target = stock.current_price * (1 + avg_sentiment * 0.2)
        elif avg_sentiment < -0.25 and sentiment_trend <= 0 and price_change_pct < 0:
            recommendation_type = 'sell'
            confidence_score = min(0.9, 0.5 + abs(avg_sentiment) * 0.5)
            reason = f"Negative sentiment ({avg_sentiment:.2f}) with downward price trend ({price_change_pct:.2f}%)."
            price_target = stock.current_price * (1 + avg_sentiment * 0.15)
        elif avg_sentiment < 0 and sentiment_trend > 0.1:
            recommendation_type = 'buy'
            confidence_score = 0.5 + sentiment_trend * 0.5
            reason = f"Improving sentiment despite negativity. Potential value buy."
            price_target = stock.current_price * (1 + sentiment_trend * 0.3)
            time_frame = 'medium-term'
        elif avg_sentiment > 0 and sentiment_trend < -0.1:
            recommendation_type = 'sell'
            confidence_score = 0.5 + abs(sentiment_trend) * 0.5
            reason = f"Worsening sentiment despite positivity. Consider selling."
            time_frame = 'short-term'
        else:
            reason = f"Mixed sentiment ({avg_sentiment:.2f}). Hold recommended."

        return {
            'stock_id': stock_id,
            'type': recommendation_type,
            'confidence_score': confidence_score,
            'reason': reason,
            'price_target': price_target,
            'time_frame': time_frame,
            'sentiment_data': {
                'avg_sentiment': avg_sentiment,
                'sentiment_trend': sentiment_trend,
                'early_sentiment': early_sentiment,
                'recent_sentiment': recent_sentiment,
            },
            'price_data': {
                'price_change_pct': price_change_pct,
                'start_price': start_price if len(price_df) > 0 else None,
                'end_price': end_price if len(price_df) > 0 else None
            }
        }

    except Exception as e:
        logger.error(f"Error generating recommendation: {str(e)}")
        return None

def generate_sentiment_only_recommendation(stock, sentiment_df):
    """Fallback if no price data is available."""
    avg_sentiment = sentiment_df['compound_score'].mean()

    recommendation_type = 'hold'
    confidence_score = 0.5
    reason = ""

    if avg_sentiment > 0.3:
        recommendation_type = 'buy'
        confidence_score = 0.5 + min(0.3, avg_sentiment * 0.3)
        reason = f"Strong positive sentiment ({avg_sentiment:.2f})."
    elif avg_sentiment < -0.3:
        recommendation_type = 'sell'
        confidence_score = 0.5 + min(0.3, abs(avg_sentiment) * 0.3)
        reason = f"Strong negative sentiment ({avg_sentiment:.2f})."
    else:
        reason = f"Neutral sentiment ({avg_sentiment:.2f})."

    return {
        'stock_id': stock.id,
        'type': recommendation_type,
        'confidence_score': confidence_score,
        'reason': reason,
        'time_frame': 'short-term',
        'sentiment_data': {
            'avg_sentiment': avg_sentiment
        }
    }

def get_top_recommendations(limit=5, user_id=None):
    """
    Generate top recommendations live based on fresh sentiment
    """
    try:
        stocks = Stock.query.all()
        recommendations = []

        for stock in stocks:
            rec = generate_recommendation(stock.id)
            if rec:
                recommendations.append(rec)

        recommendations.sort(key=lambda x: (
            1 if x['type'] == 'buy' else 0,
            x['confidence_score']
        ), reverse=True)

        return recommendations[:limit]

    except Exception as e:
        logger.error(f"Error getting top recommendations: {str(e)}")
        return []
