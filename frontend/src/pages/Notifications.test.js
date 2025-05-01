// frontend/src/pages/Notifications.test.js

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Notifications from './Notifications';
import { MemoryRouter } from 'react-router-dom';
import * as dateFns from 'date-fns';

jest.useFakeTimers();

describe('Notifications Component - Full Coverage', () => {
  const setup = () => {
    render(
      <MemoryRouter>
        <Notifications />
      </MemoryRouter>
    );
    // Fast-forward the timer to simulate API delay
    jest.runAllTimers();
  };

  test('renders loading spinner initially', () => {
    render(
      <MemoryRouter>
        <Notifications />
      </MemoryRouter>
    );
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('renders notification list correctly after loading', async () => {
    setup();
    await waitFor(() => {
      expect(screen.getByText(/Price Alert: AAPL/i)).toBeInTheDocument();
      expect(screen.getByText(/New Recommendation: MSFT/i)).toBeInTheDocument();
      expect(screen.getByText(/News Alert: TSLA/i)).toBeInTheDocument();
    });
  });

  test('handles mark as read on notification click', async () => {
    setup();
    const item = screen.getByText(/Price Alert: AAPL/i);
    fireEvent.click(item);
    const parent = item.closest('li');
    expect(parent).toHaveStyle('background-color: inherit');
  });

  test('handles delete notification click', async () => {
    setup();
    const deleteButtons = screen.getAllByLabelText(/delete/i);
    expect(deleteButtons.length).toBeGreaterThan(0);

    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(screen.queryByText(/Price Alert: AAPL/i)).not.toBeInTheDocument();
    });
  });

  test('renders empty state when no notifications exist', async () => {
    // Mock useState to simulate empty notification list
    jest.spyOn(React, 'useState')
      .mockImplementationOnce(() => [false, jest.fn()]) // loading
      .mockImplementationOnce(() => [[], jest.fn()])    // notifications
      .mockImplementationOnce(() => ['', jest.fn()]);   // error

    render(
      <MemoryRouter>
        <Notifications />
      </MemoryRouter>
    );

    expect(await screen.findByText(/No notifications/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Go to Dashboard/i })).toBeInTheDocument();
  });

  test('renders error alert and can close it', async () => {
    const mockSetError = jest.fn();
    jest.spyOn(React, 'useState')
      .mockImplementationOnce(() => [false, jest.fn()])       // loading
      .mockImplementationOnce(() => [[], jest.fn()])          // notifications
      .mockImplementationOnce(() => ['Something went wrong', mockSetError]); // error

    render(
      <MemoryRouter>
        <Notifications />
      </MemoryRouter>
    );

    const errorAlert = await screen.findByText(/Something went wrong/i);
    expect(errorAlert).toBeInTheDocument();

    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);
    expect(mockSetError).toHaveBeenCalledWith('');
  });
});
