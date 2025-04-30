# ✅ FILE: app/services/sentiment_service.py

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging
import requests
from datetime import datetime
import pandas as pd
from app.models.db import db
from app.models.stock import Stock
from app.models.sentiment import SentimentData

analyzer = SentimentIntensityAnalyzer()
logger = logging.getLogger(__name__)

def analyze_text(text):
    if not text:
        return None
    try:
        scores = analyzer.polarity_scores(text)
        compound = scores['compound']
        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'

        return {
            'compound_score': compound,
            'positive_score': scores['pos'],
            'neutral_score': scores['neu'],
            'negative_score': scores['neg'],
            'sentiment_label': label
        }
    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}")
        return None

def scrape_news(symbol, limit=5, save_to_db=True):
    """
    Scrape Yahoo Finance news for a stock symbol.
    Perform sentiment analysis and (optionally) save to DB.
    """
    try:
        base_url = f"https://query1.finance.yahoo.com/v1/finance/search?q={symbol}&newsCount={limit}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        results = response.json()

        articles = results.get("news", [])
        news_items = []

        for article in articles[:limit]:
            title = article.get("title")
            url = article.get("link")
            publisher = article.get("publisher", "Yahoo Finance")
            published_at = datetime.utcfromtimestamp(article.get("providerPublishTime", datetime.utcnow().timestamp()))

            sentiment = analyze_text(title)
            if sentiment:
                news_item = {
                    'title': title,
                    'url': url,
                    'source': publisher,
                    'published_at': published_at.isoformat(),
                    'compound_score': sentiment['compound_score'],
                    'positive_score': sentiment['positive_score'],
                    'neutral_score': sentiment['neutral_score'],
                    'negative_score': sentiment['negative_score'],
                    'sentiment_label': sentiment['sentiment_label']
                }
                news_items.append(news_item)

                # ✅ Save directly into SentimentData table if save_to_db=True
                if save_to_db:
                    stock = Stock.query.filter_by(symbol=symbol.upper()).first()
                    if not stock:
                        stock = Stock(symbol=symbol.upper(), name=f"{symbol.upper()} (auto)", sector="Unknown")
                        db.session.add(stock)
                        db.session.commit()

                # ✅ this must be outside the `if not stock` block
                    existing = SentimentData.query.filter_by(
                        stock_id=stock.id,
                        title=title,
                        url=url
                        ).first()

                    if not existing:
                        sentiment_record = SentimentData(
                            stock_id=stock.id,
                            stock_symbol=stock.symbol,  # <- this is correctly set
                            source=publisher,
                            title=title,
                            url=url,
                            compound_score=sentiment['compound_score'],
                            positive_score=sentiment['positive_score'],
                            neutral_score=sentiment['neutral_score'],
                            negative_score=sentiment['negative_score'],
                            sentiment_label=sentiment['sentiment_label'],
                            published_at=published_at
                        )
                        db.session.add(sentiment_record)


        if save_to_db:
            db.session.commit()

        return news_items

    except Exception as e:
        logger.error(f"Error scraping news for {symbol}: {str(e)}")
        return []

def aggregate_sentiment(sentiment_data):
    """
    Aggregate sentiment scores from multiple sources.
    Returns weighted average scores and sentiment summary.
    """
    if not sentiment_data:
        return None

    try:
        df = pd.DataFrame(sentiment_data)

        if 'published_at' in df.columns:
            df['published_at'] = pd.to_datetime(df['published_at'])
            now = datetime.now()
            df['age_hours'] = (now - df['published_at']).dt.total_seconds() / 3600
            df['weight'] = 1 / (1 + df['age_hours'])
            df['weight'] = df['weight'] / df['weight'].sum()

            compound_avg = (df['compound_score'] * df['weight']).sum()
            positive_avg = (df['positive_score'] * df['weight']).sum()
            neutral_avg = (df['neutral_score'] * df['weight']).sum()
            negative_avg = (df['negative_score'] * df['weight']).sum()
        else:
            compound_avg = df['compound_score'].mean()
            positive_avg = df['positive_score'].mean()
            neutral_avg = df['neutral_score'].mean()
            negative_avg = df['negative_score'].mean()

        if compound_avg >= 0.05:
            overall_sentiment = 'positive'
        elif compound_avg <= -0.05:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'

        sentiment_counts = df['sentiment_label'].value_counts().to_dict()
        total = len(df)
        sentiment_percentages = {
            'positive': sentiment_counts.get('positive', 0) / total * 100,
            'neutral': sentiment_counts.get('neutral', 0) / total * 100,
            'negative': sentiment_counts.get('negative', 0) / total * 100
        }

        return {
            'compound_score': compound_avg,
            'positive_score': positive_avg,
            'neutral_score': neutral_avg,
            'negative_score': negative_avg,
            'sentiment_label': overall_sentiment,
            'sentiment_counts': sentiment_counts,
            'sentiment_percentages': sentiment_percentages,
            'data_points': len(df),
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error aggregating sentiment: {str(e)}")
        return None



