import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import NotFound from './NotFound';
import * as reactRouterDom from 'react-router-dom';

jest.mock('react-router-dom', () => {
  const original = jest.requireActual('react-router-dom');
  return {
    ...original,
    useNavigate: jest.fn(),
  };
});

describe('NotFound Component - Full Coverage', () => {
  const mockNavigate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    reactRouterDom.useNavigate.mockReturnValue(mockNavigate);
  });

  test('renders all content and elements', () => {
    render(
      <MemoryRouter>
        <NotFound />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: /404 - Page Not Found/i })).toBeInTheDocument();
    expect(
      screen.getByText(/The page you are looking for does not exist or has been moved/i)
    ).toBeInTheDocument();

    // Check both buttons
    expect(screen.getByRole('link', { name: /go to dashboard/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /go back/i })).toBeInTheDocument();

    // Check icon
    expect(screen.getByTestId('ErrorOutlineIcon')).toBeInTheDocument();
  });

  test('navigates back when Go Back is clicked', () => {
    render(
      <MemoryRouter>
        <NotFound />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole('button', { name: /go back/i }));
    expect(mockNavigate).toHaveBeenCalledWith(-1);
  });

  test('Go to Dashboard link has correct href', () => {
    render(
      <MemoryRouter>
        <NotFound />
      </MemoryRouter>
    );

    const dashboardLink = screen.getByRole('link', { name: /go to dashboard/i });
    expect(dashboardLink).toHaveAttribute('href', '/');
  });
});
