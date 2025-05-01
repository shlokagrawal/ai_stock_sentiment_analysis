import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import StockDetails from '../pages/StockDetails';
import * as apiService from '../services/apiService';

jest.mock('../services/apiService');

const mockStock = {
  name: 'Test Company',
  symbol: 'TEST',
  current_price: 100,
  previous_close: 95,
  sector: 'Technology'
};

const mockAggregateSentiment = {
  sentiment_label: 'positive',
  compound_score: 0.8,
  positive_score: 0.6,
  neutral_score: 0.3,
  negative_score: 0.1
};

const mockSentimentData = [
  {
    id: 1,
    title: 'Stock surges amid good news',
    source: 'NewsSite',
    sentiment_label: 'positive',
    url: 'https://example.com'
  }
];

const mockRecommendation = {
  type: 'buy',
  confidence_score: 0.85,
  price_target: 120,
  time_frame: '1 month',
  reason: 'Strong earnings and analyst upgrades',
  created_at: new Date().toISOString()
};

const renderWithRoute = (stockId = 'TEST') => {
  return render(
    <MemoryRouter initialEntries={[`/stocks/${stockId}`]}>
      <Routes>
        <Route path="/stocks/:stockId" element={<StockDetails />} />
      </Routes>
    </MemoryRouter>
  );
};

describe('StockDetails Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', async () => {
    apiService.getStockBySymbol.mockResolvedValue({ success: true, stock: mockStock });
    renderWithRoute();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    await waitFor(() => screen.getByText(/test company/i));
  });

  it('displays error if stock loading fails', async () => {
    apiService.getStockBySymbol.mockRejectedValue(new Error('API error'));
    renderWithRoute();
    await waitFor(() => {
      expect(screen.getByText(/an error occurred while loading stock data/i)).toBeInTheDocument();
    });
  });

  it('shows stock overview tab by default', async () => {
    apiService.getStockBySymbol.mockResolvedValue({ success: true, stock: mockStock });
    renderWithRoute();
    expect(await screen.findByText(/Stock Overview/i)).toBeInTheDocument();
    expect(screen.getByText(/Current Price/i)).toBeInTheDocument();
    expect(screen.getByText(/Sector: Technology/i)).toBeInTheDocument();
  });

  it('loads sentiment data and displays sentiment tab', async () => {
    apiService.getStockBySymbol.mockResolvedValue({ success: true, stock: mockStock });
    apiService.getStockSentiment.mockResolvedValue({ success: true, sentimentData: mockSentimentData });
    apiService.getAggregateSentiment.mockResolvedValue({ success: true, aggregatedSentiment: mockAggregateSentiment });

    renderWithRoute();

    const sentimentTab = await screen.findByRole('tab', { name: /Sentiment Analysis/i });
    fireEvent.click(sentimentTab);

    expect(await screen.findByText(/Overall Sentiment/i)).toBeInTheDocument();
    expect(screen.getByText(/Recent News Sentiment/i)).toBeInTheDocument();
    expect(screen.getByText(/Stock surges amid good news/i)).toBeInTheDocument();
  });

  it('shows sentiment error if sentiment API fails', async () => {
    apiService.getStockBySymbol.mockResolvedValue({ success: true, stock: mockStock });
    apiService.getStockSentiment.mockRejectedValue(new Error('sentiment error'));
    apiService.getAggregateSentiment.mockRejectedValue(new Error('aggregate error'));

    renderWithRoute();

    fireEvent.click(await screen.findByRole('tab', { name: /Sentiment Analysis/i }));

    await waitFor(() => {
      expect(screen.getByText(/an error occurred while loading sentiment data/i)).toBeInTheDocument();
    });
  });

  it('loads recommendation data and displays it', async () => {
    apiService.getStockBySymbol.mockResolvedValue({ success: true, stock: mockStock });
    apiService.getStockRecommendation.mockResolvedValue({ success: true, recommendation: mockRecommendation });

    renderWithRoute();

    fireEvent.click(await screen.findByRole('tab', { name: /Recommendations/i }));

    await waitFor(() => {
      expect(screen.getByText(/Recommendation:/i)).toBeInTheDocument();
      expect(screen.getByText(/buy/i)).toBeInTheDocument();
      expect(screen.getByText(/Confidence Score:/i)).toBeInTheDocument();
      expect(screen.getByText(/Price Target:/i)).toBeInTheDocument();
    });
  });

  it('shows recommendation error if API fails', async () => {
    apiService.getStockBySymbol.mockResolvedValue({ success: true, stock: mockStock });
    apiService.getStockRecommendation.mockRejectedValue(new Error('fail'));

    renderWithRoute();

    fireEvent.click(await screen.findByRole('tab', { name: /Recommendations/i }));

    await waitFor(() => {
      expect(screen.getByText(/an error occurred while loading recommendation data/i)).toBeInTheDocument();
    });
  });

  it('handles refresh stock button click', async () => {
    apiService.getStockBySymbol.mockResolvedValue({ success: true, stock: mockStock });
    apiService.refreshStockData.mockResolvedValue({ success: true, stock: mockStock });

    renderWithRoute();

    const btn = await screen.findByRole('button', { name: /Refresh Data/i });
    fireEvent.click(btn);

    await waitFor(() => {
      expect(apiService.refreshStockData).toHaveBeenCalled();
    });
  });

  it('handles refresh sentiment button click', async () => {
    apiService.getStockBySymbol.mockResolvedValue({ success: true, stock: mockStock });
    apiService.getStockSentiment.mockResolvedValue({ success: true, sentimentData: mockSentimentData });
    apiService.getAggregateSentiment.mockResolvedValue({ success: true, aggregatedSentiment: mockAggregateSentiment });
    apiService.refreshSentiment.mockResolvedValue({ success: true });

    renderWithRoute();

    fireEvent.click(await screen.findByRole('tab', { name: /Sentiment Analysis/i }));

    const refreshBtn = await screen.findByRole('button', { name: /Refresh Sentiment Data/i });
    fireEvent.click(refreshBtn);

    await waitFor(() => {
      expect(apiService.refreshSentiment).toHaveBeenCalled();
    });
  });
});
/////////////////////// New Test Cases ///////////////////////
it('handles "No sentiment data" error by retrying with refresh', async () => {
    jest.useFakeTimers(); // control setTimeout
    apiService.getStockBySymbol.mockResolvedValue({ success: true, stock: mockStock });
  
    apiService.getStockSentiment.mockResolvedValue({
      success: false,
      error: 'No sentiment data'
    });
    apiService.getAggregateSentiment.mockResolvedValue({
      success: false,
      error: 'No sentiment data'
    });
  
    apiService.refreshSentiment.mockResolvedValue({ success: true });
  
    renderWithRoute();
  
    fireEvent.click(await screen.findByRole('tab', { name: /Sentiment Analysis/i }));
  
    await waitFor(() => {
      expect(apiService.refreshSentiment).toHaveBeenCalledWith('TEST');
    });
  
    jest.runAllTimers(); // fast-forward setTimeout
    jest.useRealTimers();
  });
  
  it('sets error if refreshSentiment fails inside handleRefreshSentiment()', async () => {
    apiService.getStockBySymbol.mockResolvedValue({ success: true, stock: mockStock });
    apiService.getStockSentiment.mockResolvedValue({ success: true, sentimentData: [] });
    apiService.getAggregateSentiment.mockResolvedValue({ success: true, aggregatedSentiment: mockAggregateSentiment });
    apiService.refreshSentiment.mockResolvedValue({ success: false });
  
    renderWithRoute();
  
    fireEvent.click(await screen.findByRole('tab', { name: /Sentiment Analysis/i }));
    const refreshBtn = await screen.findByRole('button', { name: /Refresh Sentiment Data/i });
    fireEvent.click(refreshBtn);
  
    expect(await screen.findByText(/failed to refresh sentiment data/i)).toBeInTheDocument();
  });
  
  it('sets error if refreshSentiment throws in handleRefreshSentiment()', async () => {
    apiService.getStockBySymbol.mockResolvedValue({ success: true, stock: mockStock });
    apiService.getStockSentiment.mockResolvedValue({ success: true, sentimentData: [] });
    apiService.getAggregateSentiment.mockResolvedValue({ success: true, aggregatedSentiment: mockAggregateSentiment });
    apiService.refreshSentiment.mockRejectedValue(new Error('network error'));
  
    renderWithRoute();
  
    fireEvent.click(await screen.findByRole('tab', { name: /Sentiment Analysis/i }));
    const refreshBtn = await screen.findByRole('button', { name: /Refresh Sentiment Data/i });
    fireEvent.click(refreshBtn);
  
    expect(await screen.findByText(/an error occurred while refreshing sentiment data/i)).toBeInTheDocument();
  });
  

  ////new test cases for coverage tab//
  it('handles "No aggregate sentiment data" by triggering refresh and retry', async () => {
    jest.useFakeTimers();
  
    apiService.getStockBySymbol.mockResolvedValue({ success: true, stock: mockStock });
  
    apiService.getStockSentiment.mockResolvedValue({ success: true, sentimentData: mockSentimentData });
  
    apiService.getAggregateSentiment.mockResolvedValue({
      success: false,
      error: 'No sentiment data'
    });
  
    apiService.refreshSentiment.mockResolvedValue({ success: true });
  
    renderWithRoute();
  
    fireEvent.click(await screen.findByRole('tab', { name: /Sentiment Analysis/i }));
  
    await waitFor(() => {
      expect(apiService.refreshSentiment).toHaveBeenCalledWith('TEST');
    });
  
    jest.runAllTimers();
    jest.useRealTimers();
  });
  
  it('sets recommendation error if API returns success: false', async () => {
    apiService.getStockBySymbol.mockResolvedValue({ success: true, stock: mockStock });
  
    apiService.getStockRecommendation.mockResolvedValue({
      success: false
    });
  
    renderWithRoute();
  
    fireEvent.click(await screen.findByRole('tab', { name: /Recommendations/i }));
  
    expect(await screen.findByText(/failed to load recommendation data/i)).toBeInTheDocument();
  });
  