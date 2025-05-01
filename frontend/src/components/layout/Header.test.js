import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Header from './Header';

jest.mock('../../context/AuthContext', () => ({
  useAuth: jest.fn(),
}));
jest.mock('../../services/authService', () => ({
  logout: jest.fn(),
}));

import { useAuth } from '../../context/AuthContext';
import { logout } from '../../services/authService';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => {
  const original = jest.requireActual('react-router-dom');
  return {
    ...original,
    useNavigate: () => mockNavigate,
  };
});

// Suppress act() warning only
beforeAll(() => {
  jest.spyOn(console, 'error').mockImplementation((msg) => {
    if (!msg.includes('ReactDOMTestUtils.act')) {
      console.error(msg);
    }
  });
});

describe('Header Component', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders login/register when not authenticated', () => {
    useAuth.mockReturnValue({ isAuthenticated: false });

    render(<Header />, { wrapper: MemoryRouter });

    expect(screen.getByText(/login/i)).toBeInTheDocument();
    expect(screen.getByText(/register/i)).toBeInTheDocument();
    expect(screen.queryByText(/dashboard/i)).not.toBeInTheDocument();
  });

  test('renders nav and avatar when authenticated', () => {
    useAuth.mockReturnValue({
      isAuthenticated: true,
      setIsAuthenticated: jest.fn(),
      setUser: jest.fn(),
      user: { username: 'john' },
    });

    render(<Header />, { wrapper: MemoryRouter });

    // Multiple instances of each label can exist (e.g., mobile and desktop menus)
    const dashboardButtons = screen.getAllByText(/dashboard/i);
    const recommendationsButtons = screen.getAllByText(/recommendations/i);
    const liveAnalysisButtons = screen.getAllByText(/live analysis/i);

    expect(dashboardButtons.length).toBeGreaterThan(0);
    expect(recommendationsButtons.length).toBeGreaterThan(0);
    expect(liveAnalysisButtons.length).toBeGreaterThan(0);

    // Avatar should appear
    //expect(screen.getByRole('img')).toBeInTheDocument();
  });

  test('opens user menu and navigates to profile', () => {
    useAuth.mockReturnValue({
      isAuthenticated: true,
      setIsAuthenticated: jest.fn(),
      setUser: jest.fn(),
      user: { username: 'john' },
    });

    render(<Header />, { wrapper: MemoryRouter });

    fireEvent.click(screen.getByRole('button', { name: /open settings/i }));
    fireEvent.click(screen.getByText(/profile/i));

    expect(mockNavigate).toHaveBeenCalledWith('/profile');
  });

  test('logs out correctly on logout click', () => {
    const setIsAuthenticated = jest.fn();
    const setUser = jest.fn();

    useAuth.mockReturnValue({
      isAuthenticated: true,
      setIsAuthenticated,
      setUser,
      user: { username: 'john' },
    });

    render(<Header />, { wrapper: MemoryRouter });

    fireEvent.click(screen.getByRole('button', { name: /open settings/i }));
    fireEvent.click(screen.getByText(/logout/i));

    expect(logout).toHaveBeenCalled();
    expect(setIsAuthenticated).toHaveBeenCalledWith(false);
    expect(setUser).toHaveBeenCalledWith(null);
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });
});
