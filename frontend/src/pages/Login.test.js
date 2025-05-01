import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Login from './Login';
import * as authService from '../services/authService';
import * as AuthContext from '../context/AuthContext';

// Mock navigate
const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => {
  const original = jest.requireActual('react-router-dom');
  return {
    ...original,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ state: null }),
    Link: ({ children, ...rest }) => <a {...rest}>{children}</a>,
  };
});

// Mock login API
jest.mock('../services/authService');

describe('Login Component - Full Coverage', () => {
  const mockSetAuth = jest.fn();
  const mockSetUser = jest.fn();

  const setup = () => {
    jest.spyOn(AuthContext, 'useAuth').mockReturnValue({
      setIsAuthenticated: mockSetAuth,
      setUser: mockSetUser,
    });

    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders all form fields and links', () => {
    setup();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByText(/forgot password/i)).toBeInTheDocument();
    expect(screen.getByText(/don't have an account/i)).toBeInTheDocument();
  });

  test('updates form input values', () => {
    setup();
    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'secret' } });

    expect(emailInput.value).toBe('test@example.com');
    expect(passwordInput.value).toBe('secret');
  });

  test('submits form successfully and navigates', async () => {
    authService.login.mockResolvedValue({
      success: true,
      user: { name: 'John', email: 'john@example.com' },
    });

    setup();
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'john@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'mypassword' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith('john@example.com', 'mypassword');
      expect(mockSetAuth).toHaveBeenCalledWith(true);
      expect(mockSetUser).toHaveBeenCalledWith({ name: 'John', email: 'john@example.com' });
      expect(mockNavigate).toHaveBeenCalledWith('/', { replace: true });
    });
  });

  test('shows error message when login fails', async () => {
    authService.login.mockResolvedValue({
      success: false,
      error: 'Invalid credentials',
    });

    setup();
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'fail@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpass' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() =>
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument()
    );
  });

  test('handles unexpected errors gracefully', async () => {
    authService.login.mockRejectedValue(new Error('Server down'));

    setup();
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'error@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'errorpass' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() =>
      expect(screen.getByText(/unexpected error/i)).toBeInTheDocument()
    );
  });

  test('disables submit button when submitting', async () => {
    let resolveLogin;
    authService.login.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveLogin = resolve;
        })
    );

    setup();
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'loading@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'loading123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(screen.getByRole('button')).toBeDisabled();

    resolveLogin({ success: true, user: {} });

    await waitFor(() =>
      expect(screen.getByRole('button')).not.toBeDisabled()
    );
  });
});
    