import axios from 'axios';

const API_URL = 'http://localhost:5000/api';
// Stocks API
export const getStocks = async (params = {}) => {
  try {
    const response = await axios.get(`${API_URL}/stocks`, { params });
    return { success: true, stocks: response.data.stocks };
  } catch (error) {
    console.error('Error fetching stocks:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to fetch stocks',
    };
  }
};

export const getStockById = async (stockId) => {
  try {
    const response = await axios.get(`${API_URL}/stocks/${stockId}`);
    return { success: true, stock: response.data.stock };
  } catch (error) {
    console.error(`Error fetching stock ${stockId}:`, error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to fetch stock details',
    };
  }
};

export const refreshStockData = async (stockId) => {
  try {
    const response = await axios.post(`${API_URL}/stocks/refresh/${stockId}`);
    return { success: true, stock: response.data.stock };
  } catch (error) {
    console.error(`Error refreshing stock ${stockId}:`, error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to refresh stock data',
    };
  }
};

// Watchlist API
export const getWatchlist = async () => {
  try {
    const response = await axios.get(`${API_URL}/stocks/watchlist`);
    return { success: true, watchlist: response.data.watchlist };
  } catch (error) {
    console.error('Error fetching watchlist:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to fetch watchlist',
    };
  }
};

export const addToWatchlist = async (stockId) => {
  try {
    const response = await axios.post(`${API_URL}/stocks/watchlist/${stockId}`);
    return { success: true, message: response.data.message };
  } catch (error) {
    console.error(`Error adding stock ${stockId} to watchlist:`, error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to add stock to watchlist',
    };
  }
};

export const removeFromWatchlist = async (stockId) => {
  try {
    const response = await axios.delete(`${API_URL}/stocks/watchlist/${stockId}`);
    return { success: true, message: response.data.message };
  } catch (error) {
    console.error(`Error removing stock ${stockId} from watchlist:`, error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to remove stock from watchlist',
    };
  }
};

// Sentiment API
export const analyzeSentiment = async (text) => {
  try {
    const response = await axios.post(`${API_URL}/sentiment/analyze`, { text });
    return { success: true, sentiment: response.data.sentiment };
  } catch (error) {
    console.error('Error analyzing sentiment:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to analyze sentiment',
    };
  }
};

export const getStockSentiment = async (stockId, days = 7) => {
  try {
    const response = await axios.get(`${API_URL}/sentiment/stock/${stockId}`, {
      params: { days },
    });
    return {
      success: true,
      stock: response.data.stock,
      sentimentData: response.data.sentiment_data,
      dataPoints: response.data.data_points,
    };
  } catch (error) {
    console.error(`Error fetching sentiment for stock ${stockId}:`, error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to fetch sentiment data',
    };
  }
};

export const getAggregateSentiment = async (stockId, days = 7) => {
  try {
    const response = await axios.get(`${API_URL}/sentiment/stock/${stockId}/aggregate`, {
      params: { days },
    });
    return {
      success: true,
      stock: response.data.stock,
      aggregatedSentiment: response.data.aggregated_sentiment,
    };
  } catch (error) {
    console.error(`Error fetching aggregate sentiment for stock ${stockId}:`, error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to fetch aggregated sentiment',
    };
  }
};

export const refreshSentiment = async (stockId) => {
  try {
    const response = await axios.post(`${API_URL}/sentiment/stock/${stockId}/refresh`);
    return {
      success: true,
      message: response.data.message,
      newRecords: response.data.new_records,
    };
  } catch (error) {
    console.error(`Error refreshing sentiment for stock ${stockId}:`, error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to refresh sentiment data',
    };
  }
};

// Recommendations API
export const getStockRecommendation = async (stockId, days = 7) => {
  try {
    const response = await axios.get(`${API_URL}/recommendations/stock/${stockId}`, {
      params: { days },
    });
    return {
      success: true,
      stock: response.data.stock,
      recommendation: response.data.recommendation,
      details: response.data.details,
      isCached: response.data.is_cached,
    };
  } catch (error) {
    console.error(`Error fetching recommendation for stock ${stockId}:`, error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to fetch recommendation',
    };
  }
};

export const getTopRecommendations = async (limit = 5) => {
  try {
    const response = await axios.get(`${API_URL}/recommendations/top`, {
      params: { limit },
    });
    return {
      success: true,
      topRecommendations: response.data.top_recommendations,
    };
  } catch (error) {
    console.error('Error fetching top recommendations:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to fetch top recommendations',
    };
  }
};

export const compareStocks = async (stockIds, days = 7) => {
  try {
    const response = await axios.post(`${API_URL}/recommendations/compare`, {
      stock_ids: stockIds,
      days,
    });
    return {
      success: true,
      recommendations: response.data.recommendations,
    };
  } catch (error) {
    console.error('Error comparing stocks:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to compare stocks',
    };
  }
}; 