//src/services/apiService.js
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const getToken = () => localStorage.getItem('token');

const setAuthHeader = () => {
  const token = getToken();
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }
};
setAuthHeader();

// Stocks API
export const getStocks = async (params = {}) => {
  try {
    const response = await axios.get(`${API_URL}/stocks`, { params });
    return { success: true, stocks: response.data.stocks };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to fetch stocks' };
  }
};

export const getStockBySymbol = async (symbol) => {
  try {
    const response = await axios.get(`${API_URL}/stocks/${symbol}`);
    return { success: true, stock: response.data.stock };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to fetch stock details' };
  }
};

export const refreshStockData = async (symbol) => {
  try {
    const response = await axios.post(`${API_URL}/stocks/refresh/${symbol}`);
    return { success: true, stock: response.data.stock };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to refresh stock data' };
  }
};

// Watchlist API (if still using stockId)
export const getWatchlist = async () => {
  try {
    const response = await axios.get(`${API_URL}/stocks/watchlist`);
    return { success: true, watchlist: response.data.watchlist };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to fetch watchlist' };
  }
};

export const addToWatchlist = async (stockId) => {
  try {
    const response = await axios.post(`${API_URL}/stocks/watchlist/${stockId}`);
    return { success: true, message: response.data.message };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to add to watchlist' };
  }
};

export const removeFromWatchlist = async (stockId) => {
  try {
    const response = await axios.delete(`${API_URL}/stocks/watchlist/${stockId}`);
    return { success: true, message: response.data.message };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to remove from watchlist' };
  }
};

// Sentiment API
export const analyzeSentiment = async (text) => {
  try {
    const response = await axios.post(`${API_URL}/sentiment/analyze`, { text });
    return { success: true, sentiment: response.data.sentiment };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to analyze sentiment' };
  }
};

export const getStockSentiment = async (symbol, days = 7) => {
  try {
    const response = await axios.get(`${API_URL}/sentiment/stock/${symbol}`, {
      params: { days },
    });
    return {
      success: true,
      stock: response.data.stock,
      sentimentData: response.data.sentiment_data,
      dataPoints: response.data.data_points,
    };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to fetch sentiment data' };
  }
};

export const getAggregateSentiment = async (symbol, days = 7) => {
  try {
    const response = await axios.get(`${API_URL}/sentiment/stock/${symbol}/aggregate`, {
      params: { days },
    });
    return {
      success: true,
      stock: response.data.stock,
      aggregatedSentiment: response.data.aggregated_sentiment,
    };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to fetch aggregate sentiment' };
  }
};

export const refreshSentiment = async (symbol) => {
  try {
    const response = await axios.post(`${API_URL}/sentiment/stock/${symbol}/refresh`);
    return {
      success: true,
      message: response.data.message,
      newRecords: response.data.new_items || 0,
    };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to refresh sentiment data' };
  }
};

// Recommendation API
export const getStockRecommendation = async (symbol, days = 7) => {
  try {
    const response = await axios.get(`${API_URL}/recommendations/stock/${symbol}`, {
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
    return { success: false, error: error.response?.data?.error || 'Failed to fetch recommendation' };
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
    return { success: false, error: error.response?.data?.error || 'Failed to fetch top recommendations' };
  }
};

export const compareStocks = async (symbols, days = 7) => {
  try {
    const response = await axios.post(`${API_URL}/recommendations/compare`, {
      symbols,
      days,
    });
    return {
      success: true,
      recommendations: response.data.recommendations,
    };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to compare stocks' };
  }
};

// Live Stock API
export const searchLiveStock = async (symbol) => {
  try {
    const response = await axios.post(`${API_URL}/live-stocks/search`, { symbol });
    return {
      success: true,
      stock: response.data.stock,
      source: response.data.source,
      message: response.data.message,
    };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to search for stock' };
  }
};

export const getLiveStockDetails = async (symbol) => {
  try {
    const response = await axios.get(`${API_URL}/live-stocks/details/${symbol}`);
    return {
      success: true,
      stock: response.data.stock,
      source: response.data.source,
    };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to fetch stock details' };
  }
};

export const getLiveStockHistory = async (symbol, period = '1mo') => {
  try {
    const response = await axios.get(`${API_URL}/live-stocks/history/${symbol}`, {
      params: { period },
    });
    return {
      success: true,
      symbol: response.data.symbol,
      period: response.data.period,
      history: response.data.history || [],
      source: response.data.source,
    };
  } catch (error) {
    return { success: false, error: error.response?.data?.error || 'Failed to fetch stock history' };
  }
};
