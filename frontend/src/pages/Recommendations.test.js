// frontend/src/pages/Recommendations.test.js
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import Recommendations from './Recommendations';
import { MemoryRouter } from 'react-router-dom';
import * as apiService from '../services/apiService';
import userEvent from '@testing-library/user-event';

jest.mock('../services/apiService');

describe('Recommendations Component - Full Coverage', () => {
  const mockRecommendations = [
    {
      stock: {
        id: 1,
        symbol: 'AAPL',
        name: 'Apple Inc.',
        current_price: 175.45,
      },
      recommendation: {
        type: 'buy',
        confidence_score: 0.92,
        reason: 'Strong positive sentiment from news and tweets.',
      },
    },
    {
      stock: {
        id: 2,
        symbol: 'TSLA',
        name: 'Tesla Inc.',
        current_price: 800.1,
      },
      recommendation: {
        type: 'sell',
        confidence_score: 0.88,
        reason: 'Negative sentiment due to recent news.',
      },
    },
    {
      stock: {
        id: 3,
        symbol: 'MSFT',
        name: 'Microsoft Corp.',
        current_price: 310.0,
      },
      recommendation: {
        type: 'hold',
        confidence_score: 0.67,
        reason: 'Neutral outlook from social trends.',
      },
    },
  ];

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading spinner initially', async () => {
    apiService.getTopRecommendations.mockReturnValue(new Promise(() => {})); // never resolves
    render(<Recommendations />, { wrapper: MemoryRouter });
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('renders recommendations for buy, sell, hold', async () => {
    apiService.getTopRecommendations.mockResolvedValue({
      success: true,
      topRecommendations: mockRecommendations,
    });

    render(<Recommendations />, { wrapper: MemoryRouter });

    expect(await screen.findByText('AAPL')).toBeInTheDocument();
    expect(screen.getByText('Apple Inc.')).toBeInTheDocument();
    expect(screen.getByText('BUY')).toBeInTheDocument();
    expect(screen.getByText(/92% confidence/)).toBeInTheDocument();

    expect(screen.getByText('TSLA')).toBeInTheDocument();
    expect(screen.getByText('SELL')).toBeInTheDocument();

    expect(screen.getByText('MSFT')).toBeInTheDocument();
    expect(screen.getByText('HOLD')).toBeInTheDocument();

    expect(screen.getAllByText('View Details')).toHaveLength(3);
  });

  test('shows error alert on failed API call', async () => {
    apiService.getTopRecommendations.mockRejectedValue(new Error('API failure'));

    render(<Recommendations />, { wrapper: MemoryRouter });

    expect(await screen.findByText(/an error occurred/i)).toBeInTheDocument();
  });

  test('shows fallback error if result.success is false', async () => {
    apiService.getTopRecommendations.mockResolvedValue({
      success: false,
      topRecommendations: [],
    });

    render(<Recommendations />, { wrapper: MemoryRouter });

    expect(await screen.findByText(/failed to load recommendations/i)).toBeInTheDocument();
  });

  test('shows empty state when recommendations list is empty', async () => {
    apiService.getTopRecommendations.mockResolvedValue({
      success: true,
      topRecommendations: [],
    });

    render(<Recommendations />, { wrapper: MemoryRouter });

    expect(await screen.findByText(/no recommendations available/i)).toBeInTheDocument();
  });

  test('allows user to close error alert', async () => {
    apiService.getTopRecommendations.mockResolvedValue({
      success: false,
    });

    render(<Recommendations />, { wrapper: MemoryRouter });

    const closeBtn = await screen.findByRole('button', { name: /close/i });
    userEvent.click(closeBtn);

    await waitFor(() =>
      expect(screen.queryByText(/failed to load recommendations/i)).not.toBeInTheDocument()
    );
  });
});
