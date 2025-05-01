import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import { useAuth } from '../context/AuthContext';
import * as apiService from '../services/apiService';

jest.mock('../context/AuthContext');
jest.mock('../services/apiService');

const mockUser = { username: 'Arpit' };

describe('Dashboard Full Coverage', () => {
  beforeEach(() => {
    useAuth.mockReturnValue({ user: mockUser });
    jest.clearAllMocks();
  });

  test('loads top recommendations and displays watchlist', async () => {
    const topStocks = [
      {
        stock: {
          id: 1,
          symbol: 'AAPL',
          name: 'Apple Inc.',
          current_price: 150.0,
        },
        recommendation: {
          type: 'buy',
          confidence_score: 0.85,
          reason: 'Strong Q2 earnings.',
        },
      },
      {
        stock: {
          id: 2,
          symbol: 'TSLA',
          name: 'Tesla Inc.',
          current_price: 720.0,
        },
        recommendation: {
          type: 'sell',
          confidence_score: 0.7,
          reason: 'Regulatory challenges.',
        },
      },
    ];

    const watchlist = [
      {
        id: 1,
        symbol: 'AAPL',
        name: 'Apple Inc.',
        current_price: 150.0,
        previous_close: 148.5,
        sector: 'Technology',
      },
    ];

    apiService.getTopRecommendations.mockResolvedValue({
      success: true,
      topRecommendations: topStocks,
    });

    apiService.getWatchlist.mockResolvedValue({
      success: true,
      watchlist,
    });

    render(
      <Router>
        <Dashboard />
      </Router>
    );

    await waitFor(() => expect(screen.getByText('AAPL')).toBeInTheDocument());
    expect(screen.getByText('Tesla Inc.')).toBeInTheDocument();
    expect(screen.getByText('Strong Q2 earnings.')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Your Watchlist'));
    await waitFor(() => screen.getByText('Sector: Technology'));
  });

  test('handles API errors gracefully', async () => {
    apiService.getTopRecommendations.mockRejectedValue(new Error('Network Error'));
    apiService.getWatchlist.mockRejectedValue(new Error('Network Error'));

    render(
      <Router>
        <Dashboard />
      </Router>
    );

    await waitFor(() => expect(screen.getByText(/Failed to load dashboard data/i)));
  });

  test('adds and removes from watchlist correctly', async () => {
    const googStock = {
      id: 3,
      symbol: 'GOOG',
      name: 'Alphabet Inc.',
      current_price: 2800,
      previous_close: 2750,
      sector: 'Technology',
    };

    // Step 1: Initial load
    apiService.getTopRecommendations.mockResolvedValue({
      success: true,
      topRecommendations: [
        {
          stock: googStock,
          recommendation: {
            type: 'hold',
            confidence_score: 0.65,
            reason: 'Market uncertainty.',
          },
        },
      ],
    });

    // Initially not in watchlist
    apiService.getWatchlist
      .mockResolvedValueOnce({ success: true, watchlist: [] }) // First load
      .mockResolvedValueOnce({ success: true, watchlist: [googStock] }) // After add
      .mockResolvedValueOnce({ success: true, watchlist: [] }); // After remove

    apiService.addToWatchlist.mockResolvedValue({ success: true });
    apiService.removeFromWatchlist.mockResolvedValue({ success: true });

    render(
      <Router>
        <Dashboard />
      </Router>
    );

    await waitFor(() => screen.getByText('GOOG'));

    // Add to watchlist
    const addButton = screen.getByRole('button', { name: /add to watchlist/i });
    fireEvent.click(addButton);
    await waitFor(() => expect(apiService.addToWatchlist).toHaveBeenCalled());

    // Switch to watchlist tab
    fireEvent.click(screen.getByText('Your Watchlist'));
    await waitFor(() => screen.getByText('GOOG'));

    // Remove from watchlist
    const removeButton = screen.getByRole('button', { name: /remove/i });
    fireEvent.click(removeButton);
    await waitFor(() => expect(apiService.removeFromWatchlist).toHaveBeenCalled());
  });
});
