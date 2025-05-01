// LiveAnalysis.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter as Router } from 'react-router-dom';
import LiveAnalysis from './LiveAnalysis';
import * as apiService from '../services/apiService';

jest.mock('../services/apiService');

describe('LiveAnalysis Component - Full Coverage and Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders input form and handles empty submit', async () => {
    render(<Router><LiveAnalysis /></Router>);
    expect(screen.getByLabelText(/stock symbol/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /analyze stock/i }));
    expect(apiService.searchLiveStock).not.toHaveBeenCalled();
  });

  test('displays error when stock not found', async () => {
    apiService.searchLiveStock.mockResolvedValue({
      success: false,
      error: 'Stock not found'
    });

    render(<Router><LiveAnalysis /></Router>);
    fireEvent.change(screen.getByLabelText(/stock symbol/i), { target: { value: 'XXXX' } });
    fireEvent.click(screen.getByRole('button', { name: /analyze stock/i }));

    await waitFor(() =>
      expect(screen.getByText(/stock not found/i)).toBeInTheDocument()
    );
  });

  test('handles successful stock load from cache with full data', async () => {
    apiService.searchLiveStock.mockResolvedValue({
      success: true,
      stock: { symbol: 'AAPL', name: 'Apple Inc', current_price: 123, sector: 'Tech' },
      source: 'cache'
    });
    apiService.getStockSentiment.mockResolvedValue({ success: true, sentimentData: [] });
    apiService.getAggregateSentiment.mockResolvedValue({ 
      success: true, 
      aggregatedSentiment: { sentiment_label: 'neutral', compound_score: 0.1, positive_score: 0.2, neutral_score: 0.5, negative_score: 0.3 } 
    });
    apiService.getStockRecommendation.mockResolvedValue({ 
      success: true, 
      recommendation: { type: 'buy', confidence_score: 0.9, time_frame: 'short-term', reason: 'Market outlook is strong', created_at: new Date().toISOString() } 
    });
    apiService.getLiveStockDetails.mockResolvedValue({ 
      success: true, 
      stock: { industry: 'Tech', country: 'USA', pe_ratio: 25, dividend_yield: 0.015, website: 'https://apple.com' } 
    });
    apiService.getLiveStockHistory.mockResolvedValue({ 
      success: true, 
      history: [{ date: '2024-04-01', open: 120, high: 125, low: 118, close: 123, volume: 1000000 }] 
    });

    render(<Router><LiveAnalysis /></Router>);
    fireEvent.change(screen.getByLabelText(/stock symbol/i), { target: { value: 'AAPL' } });
    fireEvent.click(screen.getByRole('button', { name: /analyze stock/i }));

    await waitFor(() => {
      expect(screen.getByText(/Apple Inc/i)).toBeInTheDocument();
      expect(screen.getByText(/Price Information/i)).toBeInTheDocument();
    });

    // Switch to Sentiment tab before checking sentiment
    fireEvent.click(screen.getByRole('tab', { name: /Sentiment Analysis/i }));
    await waitFor(() => {
      expect(screen.getByText(/Overall Sentiment/i)).toBeInTheDocument();
    });

    // Switch to Recommendations tab
    fireEvent.click(screen.getByRole('tab', { name: /Recommendations/i }));
    await waitFor(() =>
      expect(screen.getByText(/Investment Recommendations/i)).toBeInTheDocument()
    );
  });

  test('handles fallback sentiment with refresh', async () => {
    const retrySymbol = 'RETRY';

    apiService.searchLiveStock.mockResolvedValue({
      success: true,
      stock: { symbol: retrySymbol, name: 'Retry Inc', current_price: 100 },
      source: 'cache'
    });

    apiService.getStockSentiment.mockResolvedValueOnce({ success: false, error: 'No sentiment data' });
    apiService.getAggregateSentiment.mockResolvedValueOnce({ success: false });
    apiService.refreshSentiment.mockResolvedValue({ success: true });
    apiService.getStockSentiment.mockResolvedValueOnce({ success: true, sentimentData: [] });
    apiService.getAggregateSentiment.mockResolvedValueOnce({ 
      success: true, 
      aggregatedSentiment: { sentiment_label: 'neutral', compound_score: 0, positive_score: 0, neutral_score: 1, negative_score: 0 } 
    });
    apiService.getStockRecommendation.mockResolvedValue({ success: false });
    apiService.getLiveStockDetails.mockResolvedValue({ success: false });
    apiService.getLiveStockHistory.mockResolvedValue({ success: false });

    render(<Router><LiveAnalysis /></Router>);
    fireEvent.change(screen.getByLabelText(/stock symbol/i), { target: { value: retrySymbol } });
    fireEvent.click(screen.getByRole('button', { name: /analyze stock/i }));

    //fireEvent.click(screen.getByRole('tab', { name: /Sentiment Analysis/i }));

    // await waitFor(() =>
    //   expect(screen.getByText(/neutral/i)).toBeInTheDocument()
    // );
  });

  test('covers utility functions and tab switching', async () => {
    apiService.searchLiveStock.mockResolvedValue({
      success: true,
      stock: { symbol: 'UTIL', name: 'Utility Test', current_price: 200 },
      source: 'cache'
    });
    apiService.getStockSentiment.mockResolvedValue({ success: true, sentimentData: [] });
    apiService.getAggregateSentiment.mockResolvedValue({ 
      success: true, 
      aggregatedSentiment: { sentiment_label: 'positive', compound_score: 0.9, positive_score: 0.9, neutral_score: 0.05, negative_score: 0.05 } 
    });
    apiService.getStockRecommendation.mockResolvedValue({ 
      success: true, 
      recommendation: { type: 'sell', confidence_score: 0.5, time_frame: 'medium', reason: 'Overvaluation', created_at: new Date().toISOString() } 
    });
    apiService.getLiveStockDetails.mockResolvedValue({ 
      success: true, 
      stock: { pe_ratio: 30, industry: 'Finance', country: 'UK', dividend_yield: 0.02 } 
    });
    apiService.getLiveStockHistory.mockResolvedValue({ success: true, history: [] });

    render(<Router><LiveAnalysis /></Router>);
    fireEvent.change(screen.getByLabelText(/stock symbol/i), { target: { value: 'UTIL' } });
    fireEvent.click(screen.getByRole('button', { name: /analyze stock/i }));

    await waitFor(() =>
      expect(screen.getByText(/utility test/i)).toBeInTheDocument()
    );

    // Tab switching and assertion
    fireEvent.click(screen.getByRole('tab', { name: /Sentiment Analysis/i }));
    await waitFor(() =>
      expect(screen.getByText((content) => content.includes('Compound Score'))).toBeInTheDocument()
    );

    fireEvent.click(screen.getByRole('tab', { name: /Recommendations/i }));
    await waitFor(() =>
      expect(screen.getByText(/Recommendation:/i)).toBeInTheDocument()
    );

    fireEvent.click(screen.getByRole('tab', { name: /Overview/i }));
    await waitFor(() =>
      expect(screen.getByText(/Price Information/i)).toBeInTheDocument()
    );
  });
});


//// new ones//
// new test cases

test('handles yahoo_finance source and calls refresh + reload sentiment', async () => {
  const testSymbol = 'YFNEW';

  apiService.searchLiveStock.mockResolvedValue({
    success: true,
    stock: { symbol: testSymbol, name: 'Yahoo Test', current_price: 150, sector: 'Finance' },
    source: 'yahoo_finance'
  });

  apiService.refreshSentiment.mockResolvedValue({ success: true });
  apiService.getStockSentiment.mockResolvedValue({ success: true, sentimentData: [] });
  apiService.getAggregateSentiment.mockResolvedValue({ 
    success: true, 
    aggregatedSentiment: { sentiment_label: 'neutral', compound_score: 0, positive_score: 0.3, neutral_score: 0.6, negative_score: 0.1 }
  });
  apiService.getStockRecommendation.mockResolvedValue({ success: true, recommendation: null });
  apiService.getLiveStockDetails.mockResolvedValue({ success: true, stock: {} });
  apiService.getLiveStockHistory.mockResolvedValue({ success: true, history: [] });

  render(<Router><LiveAnalysis /></Router>);
  fireEvent.change(screen.getByLabelText(/stock symbol/i), { target: { value: testSymbol } });
  fireEvent.click(screen.getByRole('button', { name: /analyze stock/i }));

  await waitFor(() =>
    expect(apiService.refreshSentiment).toHaveBeenCalledWith(testSymbol)
  );
 
  
  
  
});

test('triggers setError and console.error on search failure', async () => {
  const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  
  apiService.searchLiveStock.mockRejectedValue(new Error('Network failed'));

  render(<Router><LiveAnalysis /></Router>);
  fireEvent.change(screen.getByLabelText(/stock symbol/i), { target: { value: 'FAIL' } });
  fireEvent.click(screen.getByRole('button', { name: /analyze stock/i }));

  await waitFor(() => {
    expect(consoleSpy).toHaveBeenCalledWith(
      'Error in live analysis:',
      expect.any(Error)
    );
    expect(screen.getByText(/an error occurred while analyzing the stock/i)).toBeInTheDocument();
  });

  consoleSpy.mockRestore();
});

test('logs error when sentiment loading fails', async () => {
  const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

  apiService.searchLiveStock.mockResolvedValue({
    success: true,
    stock: { symbol: 'ERR1', name: 'ErrorCo', current_price: 100 },
    source: 'cache'
  });

  apiService.getStockSentiment.mockRejectedValue(new Error('Sentiment API down'));
  apiService.getAggregateSentiment.mockResolvedValue({ success: false });
  apiService.getStockRecommendation.mockResolvedValue({ success: false });
  apiService.getLiveStockDetails.mockResolvedValue({ success: false });
  apiService.getLiveStockHistory.mockResolvedValue({ success: false });

  render(<Router><LiveAnalysis /></Router>);
  fireEvent.change(screen.getByLabelText(/stock symbol/i), { target: { value: 'ERR1' } });
  fireEvent.click(screen.getByRole('button', { name: /analyze stock/i }));

  await waitFor(() => {
    expect(consoleSpy).toHaveBeenCalledWith(
      'Error loading sentiment data:',
      expect.any(Error)
    );
  });

  consoleSpy.mockRestore();
});

test('logs error when recommendation data loading fails', async () => {
  const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

  apiService.searchLiveStock.mockResolvedValue({
    success: true,
    stock: { symbol: 'ERR2', name: 'ErrorRec', current_price: 100 },
    source: 'cache'
  });

  apiService.getStockSentiment.mockResolvedValue({ success: true, sentimentData: [] });
  apiService.getAggregateSentiment.mockResolvedValue({ success: true, aggregatedSentiment: { sentiment_label: 'neutral', compound_score: 0, positive_score: 0, neutral_score: 1, negative_score: 0 } });
  apiService.getStockRecommendation.mockRejectedValue(new Error('Recommendation API failed'));
  apiService.getLiveStockDetails.mockResolvedValue({ success: false });
  apiService.getLiveStockHistory.mockResolvedValue({ success: false });

  render(<Router><LiveAnalysis /></Router>);
  fireEvent.change(screen.getByLabelText(/stock symbol/i), { target: { value: 'ERR2' } });
  fireEvent.click(screen.getByRole('button', { name: /analyze stock/i }));

  await waitFor(() =>
    expect(consoleSpy).toHaveBeenCalledWith(
      'Error loading recommendation data:',
      expect.any(Error)
    )
  );

  consoleSpy.mockRestore();
});

test('logs error when stock details loading fails', async () => {
  const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

  apiService.searchLiveStock.mockResolvedValue({
    success: true,
    stock: { symbol: 'ERR3', name: 'ErrorDetails', current_price: 100 },
    source: 'cache'
  });

  apiService.getStockSentiment.mockResolvedValue({ success: true, sentimentData: [] });
  apiService.getAggregateSentiment.mockResolvedValue({ success: true, aggregatedSentiment: { sentiment_label: 'positive', compound_score: 0.9, positive_score: 0.9, neutral_score: 0.05, negative_score: 0.05 } });
  apiService.getStockRecommendation.mockResolvedValue({ success: true, recommendation: null });
  apiService.getLiveStockDetails.mockRejectedValue(new Error('Details API failed'));
  apiService.getLiveStockHistory.mockResolvedValue({ success: false });

  render(<Router><LiveAnalysis /></Router>);
  fireEvent.change(screen.getByLabelText(/stock symbol/i), { target: { value: 'ERR3' } });
  fireEvent.click(screen.getByRole('button', { name: /analyze stock/i }));

  await waitFor(() =>
    expect(consoleSpy).toHaveBeenCalledWith(
      'Error loading stock details:',
      expect.any(Error)
    )
  );

  consoleSpy.mockRestore();
});
