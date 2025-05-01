// src/pages/Profile.test.js

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import Profile from './Profile';
import { MemoryRouter } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import * as authService from '../services/authService';

jest.mock('../context/AuthContext', () => ({
  useAuth: jest.fn(),
}));

jest.mock('../services/authService', () => ({
  getUserProfile: jest.fn(),
  updateUserProfile: jest.fn(),
  logout: jest.fn(),
}));

describe('Profile Component', () => {
  const mockSetUser = jest.fn();
  const mockSetIsAuthenticated = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();

    useAuth.mockReturnValue({
      user: { username: 'testuser', email: 'test@example.com', role: 'user' },
      setUser: mockSetUser,
      setIsAuthenticated: mockSetIsAuthenticated,
    });

    authService.getUserProfile.mockResolvedValue({
      success: true,
      user: { username: 'testuser', email: 'test@example.com' },
    });
  });

  test('renders loading and then form with user data', async () => {
    render(<Profile />, { wrapper: MemoryRouter });

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    expect(await screen.findByDisplayValue('testuser')).toBeInTheDocument();
    expect(screen.getByDisplayValue('test@example.com')).toBeInTheDocument();
  });

  test('shows error if passwords do not match', async () => {
    render(<Profile />, { wrapper: MemoryRouter });

    await screen.findByDisplayValue('testuser');

    await act(async () => {
      fireEvent.change(screen.getByLabelText('New Password', { selector: 'input[name="password"]' }), {
        target: { value: 'pass1' },
      });
      fireEvent.change(screen.getByLabelText('Confirm New Password', { selector: 'input[name="confirmPassword"]' }), {
        target: { value: 'pass2' },
      });
      fireEvent.click(screen.getByText(/Save Changes/i));
    });

    expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
  });

  test('submits profile update without password', async () => {
    authService.updateUserProfile.mockResolvedValue({
      success: true,
      user: { username: 'testuser', email: 'test@example.com' },
    });

    render(<Profile />, { wrapper: MemoryRouter });

    await screen.findByDisplayValue('testuser');

    await act(async () => {
      fireEvent.click(screen.getByText(/Save Changes/i));
    });

    await waitFor(() =>
      expect(
        screen.getByText((text) => text.includes('Profile updated successfully'))
      ).toBeInTheDocument()
    );
  });

  test('submits profile update with password', async () => {
    authService.updateUserProfile.mockResolvedValue({
      success: true,
      user: { username: 'testuser', email: 'test@example.com' },
    });

    render(<Profile />, { wrapper: MemoryRouter });

    await screen.findByDisplayValue('testuser');

    await act(async () => {
      fireEvent.change(screen.getByLabelText('New Password', { selector: 'input[name="password"]' }), {
        target: { value: 'secret' },
      });
      fireEvent.change(screen.getByLabelText('Confirm New Password', { selector: 'input[name="confirmPassword"]' }), {
        target: { value: 'secret' },
      });
      fireEvent.click(screen.getByText(/Save Changes/i));
    });

    await waitFor(() =>
      expect(
        screen.getByText((text) => text.includes('Profile updated successfully'))
      ).toBeInTheDocument()
    );
  });

  test('shows error from API failure', async () => {
    authService.updateUserProfile.mockResolvedValue({
      success: false,
      error: 'Update failed',
    });

    render(<Profile />, { wrapper: MemoryRouter });

    await screen.findByDisplayValue('testuser');

    await act(async () => {
      fireEvent.click(screen.getByText(/Save Changes/i));
    });

    await waitFor(() => {
      expect(screen.getByText('Update failed')).toBeInTheDocument();
    });
  });

  test('handles fetch profile failure', async () => {
    authService.getUserProfile.mockRejectedValue(new Error('Failed'));

    render(<Profile />, { wrapper: MemoryRouter });

    await waitFor(() =>
      expect(screen.getByText('An error occurred while loading your profile')).toBeInTheDocument()
    );
  });

  test('handles logout', async () => {
    render(<Profile />, { wrapper: MemoryRouter });

    await screen.findByDisplayValue('testuser');

    fireEvent.click(screen.getByText(/Logout/i));

    expect(authService.logout).toHaveBeenCalled();
    expect(mockSetIsAuthenticated).toHaveBeenCalledWith(false);
    expect(mockSetUser).toHaveBeenCalledWith(null);
  });
});
