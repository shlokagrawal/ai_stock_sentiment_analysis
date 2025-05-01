import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Notifications from './Notifications';

describe('Notifications Component - Stable Tests', () => {
  beforeEach(async () => {
    jest.useFakeTimers(); // Simulate time-based delay
    render(
      <MemoryRouter>
        <Notifications />
      </MemoryRouter>
    );
    jest.advanceTimersByTime(1000); // Trigger mockNotifications loading
    await waitFor(() => screen.getByText('Price Alert: AAPL'));
  });

  test('renders notification titles after loading', async () => {
    expect(screen.getByText('Price Alert: AAPL')).toBeInTheDocument();
    expect(screen.getByText('New Recommendation: MSFT')).toBeInTheDocument();
    expect(screen.getByText('News Alert: TSLA')).toBeInTheDocument();
  });

  test('allows deleting a notification', async () => {
    const deleteButtons = screen.getAllByLabelText('delete');
    fireEvent.click(deleteButtons[0]);
    await waitFor(() =>
      expect(screen.queryByText('Price Alert: AAPL')).not.toBeInTheDocument()
    );
  });

  test('shows empty state after deleting all notifications', async () => {
    const deleteButtons = screen.getAllByLabelText('delete');
    deleteButtons.forEach((btn) => fireEvent.click(btn));
    await waitFor(() =>
      expect(screen.getByText(/no notifications/i)).toBeInTheDocument()
    );
  });
});
