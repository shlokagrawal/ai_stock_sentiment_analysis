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
    
    Args:
        stock_id (int): Stock ID
        days (int): Number of days of historical data to consider
        
    Returns:
        dict: Recommendation data
    """
    try:
        # Get stock information
        stock = Stock.query.get(stock_id)
        if not stock:
            logger.error(f"Stock with ID {stock_id} not found")
            return None
        
        # Get sentiment data for the specified period
        from_date = datetime.utcnow() - timedelta(days=days)
        
        sentiment_records = SentimentData.query.filter_by(
            stock_id=stock_id
        ).filter(
            SentimentData.created_at >= from_date
        ).all()
        
        if not sentiment_records:
            logger.warning(f"No sentiment data available for stock {stock.symbol}")
            return {
                'stock_id': stock_id,
                'type': 'hold',
                'confidence_score': 0.5,
                'reason': f"Insufficient sentiment data for {stock.symbol}. Need more information to make a recommendation.",
                'time_frame': 'short-term'
            }
        
        # Convert to DataFrame for analysis
        sentiment_df = pd.DataFrame([
            {
                'compound_score': record.compound_score,
                'sentiment_label': record.sentiment_label,
                'created_at': record.created_at
            }
            for record in sentiment_records
        ])
        
        # Get historical price data
        historical_data = get_historical_data(stock.symbol, period='1mo')
        
        if not historical_data:
            logger.warning(f"No historical price data available for stock {stock.symbol}")
            
            # Make recommendation based solely on sentiment
            return generate_sentiment_only_recommendation(stock, sentiment_df)
        
        # Convert historical data to DataFrame
        price_df = pd.DataFrame(historical_data)
        price_df['date'] = pd.to_datetime(price_df['date'])
        price_df = price_df.sort_values('date')
        
        # Calculate price trend
        if len(price_df) >= 2:
            start_price = price_df.iloc[0]['close']
            end_price = price_df.iloc[-1]['close']
            price_change_pct = (end_price - start_price) / start_price * 100
        else:
            price_change_pct = 0
        
        # Calculate sentiment trend
        sentiment_df['created_at'] = pd.to_datetime(sentiment_df['created_at'])
        sentiment_df = sentiment_df.sort_values('created_at')
        
        # Split into two periods to compare trend
        if len(sentiment_df) >= 4:
            mid_idx = len(sentiment_df) // 2
            early_sentiment = sentiment_df.iloc[:mid_idx]['compound_score'].mean()
            recent_sentiment = sentiment_df.iloc[mid_idx:]['compound_score'].mean()
            sentiment_trend = recent_sentiment - early_sentiment
        else:
            sentiment_trend = 0
            early_sentiment = sentiment_df['compound_score'].mean()
            recent_sentiment = early_sentiment
        
        # Overall sentiment
        avg_sentiment = sentiment_df['compound_score'].mean()
        
        # Generate recommendation
        recommendation_type = 'hold'
        confidence_score = 0.5
        reason = ""
        price_target = None
        time_frame = 'short-term'
        
        # Bullish case
        if avg_sentiment > 0.25 and sentiment_trend >= 0 and price_change_pct > 0:
            recommendation_type = 'buy'
            confidence_score = min(0.9, 0.5 + avg_sentiment * 0.5)
            reason = f"Strong positive sentiment ({avg_sentiment:.2f}) with improving trend. Stock price has increased by {price_change_pct:.2f}% recently."
            price_target = stock.current_price * (1 + avg_sentiment * 0.2)
            
        # Bearish case
        elif avg_sentiment < -0.25 and sentiment_trend <= 0 and price_change_pct < 0:
            recommendation_type = 'sell'
            confidence_score = min(0.9, 0.5 + abs(avg_sentiment) * 0.5)
            reason = f"Strong negative sentiment ({avg_sentiment:.2f}) with worsening trend. Stock price has decreased by {abs(price_change_pct):.2f}% recently."
            price_target = stock.current_price * (1 + avg_sentiment * 0.15)
            
        # Contrarian buy (negative sentiment but improving)
        elif avg_sentiment < 0 and sentiment_trend > 0.1:
            recommendation_type = 'buy'
            confidence_score = 0.5 + sentiment_trend * 0.5
            reason = f"Currently negative sentiment ({avg_sentiment:.2f}) but showing significant improvement. Potential value opportunity."
            price_target = stock.current_price * (1 + sentiment_trend * 0.3)
            time_frame = 'medium-term'
            
        # Contrarian sell (positive sentiment but worsening)
        elif avg_sentiment > 0 and sentiment_trend < -0.1:
            recommendation_type = 'sell'
            confidence_score = 0.5 + abs(sentiment_trend) * 0.5
            reason = f"Currently positive sentiment ({avg_sentiment:.2f}) but showing significant deterioration. Consider locking in profits."
            time_frame = 'short-term'
            
        # Momentum buy
        elif avg_sentiment > 0 and price_change_pct > 5:
            recommendation_type = 'buy'
            confidence_score = 0.6
            reason = f"Positive sentiment ({avg_sentiment:.2f}) with strong price momentum. Stock price has increased by {price_change_pct:.2f}% recently."
            price_target = stock.current_price * 1.1
            
        # Momentum sell
        elif avg_sentiment < 0 and price_change_pct < -5:
            recommendation_type = 'sell'
            confidence_score = 0.6
            reason = f"Negative sentiment ({avg_sentiment:.2f}) with downward price momentum. Stock price has decreased by {abs(price_change_pct):.2f}% recently."
            
        # Neutral/Hold
        else:
            reason = f"Mixed signals with sentiment at {avg_sentiment:.2f} and price change of {price_change_pct:.2f}%. Recommend holding until clearer trend emerges."
        
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
                'start_price': price_df.iloc[0]['close'] if len(price_df) > 0 else None,
                'end_price': price_df.iloc[-1]['close'] if len(price_df) > 0 else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendation: {str(e)}")
        return None

def generate_sentiment_only_recommendation(stock, sentiment_df):
    """Generate recommendation based solely on sentiment data when price data is unavailable"""
    avg_sentiment = sentiment_df['compound_score'].mean()
    
    recommendation_type = 'hold'
    confidence_score = 0.5
    reason = ""
    
    if avg_sentiment > 0.3:
        recommendation_type = 'buy'
        confidence_score = 0.5 + min(0.3, avg_sentiment * 0.3)
        reason = f"Strong positive sentiment ({avg_sentiment:.2f}) for {stock.symbol}. Consider buying based on sentiment alone."
    elif avg_sentiment < -0.3:
        recommendation_type = 'sell'
        confidence_score = 0.5 + min(0.3, abs(avg_sentiment) * 0.3)
        reason = f"Strong negative sentiment ({avg_sentiment:.2f}) for {stock.symbol}. Consider selling based on sentiment alone."
    else:
        reason = f"Neutral sentiment ({avg_sentiment:.2f}) for {stock.symbol}. Hold position or seek additional information."
    
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
    Get top stock recommendations based on sentiment analysis
    
    Args:
        limit (int): Maximum number of recommendations to return
        user_id (int): User ID to consider watchlist preferences
        
    Returns:
        list: Top stock recommendations
    """
    # Get all active stocks
    stocks = Stock.query.all()
    
    recommendations = []
    
    for stock in stocks[:10]:  # Limit processing to 10 stocks for demo purposes
        recommendation = generate_recommendation(stock.id)
        if recommendation:
            recommendations.append(recommendation)
    
    # Sort by confidence score and recommendation type
    # Prioritize high-confidence buys
    recommendations.sort(key=lambda x: (
        1 if x['type'] == 'buy' else 0,
        x['confidence_score']
    ), reverse=True)
    
    return recommendations[:limit] 