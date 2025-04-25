from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
import logging
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pandas as pd
import re

# Initialize VADER
analyzer = SentimentIntensityAnalyzer()

# Setup logging
logger = logging.getLogger(__name__)

def download_nltk_data():
    """Download required NLTK data"""
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
    except Exception as e:
        logger.error(f"Error downloading NLTK data: {str(e)}")

def analyze_text(text):
    """
    Analyze sentiment of text using VADER
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Sentiment scores and label
    """
    if not text:
        return None
    
    try:
        # Get sentiment scores
        scores = analyzer.polarity_scores(text)
        
        # Determine sentiment label
        compound = scores['compound']
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'compound_score': scores['compound'],
            'positive_score': scores['pos'],
            'neutral_score': scores['neu'],
            'negative_score': scores['neg'],
            'sentiment_label': sentiment
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        return None

def scrape_news(symbol, limit=5):
    """
    Scrape news articles for a stock symbol
    
    Args:
        symbol (str): Stock ticker symbol
        limit (int): Maximum number of articles to scrape
        
    Returns:
        list: List of news articles with sentiment analysis
    """
    try:
        # For a real implementation, you would use a news API or web scraping
        # This is a simplified version that would need to be expanded
        
        # Example URL: Yahoo Finance news
        url = f"https://finance.yahoo.com/quote/{symbol}/news"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        news_items = []
        
        # Find news articles (this needs to be adapted based on the actual HTML structure)
        articles = soup.find_all('div', {'class': 'Ov(h)'})
        
        for article in articles[:limit]:
            try:
                # Extract title and link
                title_element = article.find('h3')
                if not title_element:
                    continue
                    
                title = title_element.text.strip()
                
                link_element = article.find('a')
                if not link_element:
                    continue
                    
                link = "https://finance.yahoo.com" + link_element.get('href')
                
                # Get the publish date if available
                time_element = article.find('div', {'class': 'C(#959595)'})
                published_at = datetime.now()
                if time_element:
                    time_text = time_element.text.strip()
                    # Parse time text (this is simplified)
                    published_at = datetime.now()  # Default to now
                
                # Analyze sentiment of title
                sentiment = analyze_text(title)
                
                if sentiment:
                    news_item = {
                        'title': title,
                        'url': link,
                        'source': 'Yahoo Finance',
                        'published_at': published_at.isoformat(),
                        'compound_score': sentiment['compound_score'],
                        'positive_score': sentiment['positive_score'],
                        'neutral_score': sentiment['neutral_score'],
                        'negative_score': sentiment['negative_score'],
                        'sentiment_label': sentiment['sentiment_label']
                    }
                    
                    news_items.append(news_item)
            except Exception as e:
                logger.error(f"Error processing news article: {str(e)}")
                continue
        
        return news_items
    
    except Exception as e:
        logger.error(f"Error scraping news for {symbol}: {str(e)}")
        return []

def aggregate_sentiment(sentiment_data):
    """
    Aggregate sentiment scores from multiple sources
    
    Args:
        sentiment_data (list): List of sentiment data items
        
    Returns:
        dict: Aggregated sentiment data
    """
    if not sentiment_data:
        return None
    
    try:
        # Convert to DataFrame for easier aggregation
        df = pd.DataFrame(sentiment_data)
        
        # Compute weighted average based on recency (if timestamp available)
        if 'published_at' in df.columns:
            df['published_at'] = pd.to_datetime(df['published_at'])
            now = datetime.now()
            df['age_hours'] = (now - df['published_at']).dt.total_seconds() / 3600
            df['weight'] = 1 / (1 + df['age_hours'])
            
            # Normalize weights
            df['weight'] = df['weight'] / df['weight'].sum()
            
            # Compute weighted scores
            compound_avg = (df['compound_score'] * df['weight']).sum()
            positive_avg = (df['positive_score'] * df['weight']).sum()
            neutral_avg = (df['neutral_score'] * df['weight']).sum()
            negative_avg = (df['negative_score'] * df['weight']).sum()
        else:
            # Simple average if no timestamps
            compound_avg = df['compound_score'].mean()
            positive_avg = df['positive_score'].mean()
            neutral_avg = df['neutral_score'].mean()
            negative_avg = df['negative_score'].mean()
        
        # Determine overall sentiment
        if compound_avg >= 0.05:
            overall_sentiment = 'positive'
        elif compound_avg <= -0.05:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        # Count by sentiment label
        sentiment_counts = df['sentiment_label'].value_counts().to_dict()
        
        # Compute percentages
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