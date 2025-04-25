import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const API_URL = 'http://localhost:5000/api/auth';

// Helper to get token from local storage
const getToken = () => {
  return localStorage.getItem('token');
};

// Helper to set token in local storage
const setToken = (token) => {
  localStorage.setItem('token', token);
};

// Helper to remove token from local storage
const removeToken = () => {
  localStorage.removeItem('token');
};

// Check if token is valid
const isTokenValid = (token) => {
  if (!token) return false;
  
  try {
    const decoded = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    
    return decoded.exp > currentTime;
  } catch (error) {
    console.error('Error decoding token:', error);
    return false;
  }
};

// Register new user
export const register = async (username, email, password) => {
  try {
    const response = await axios.post(`${API_URL}/register`, {
      username,
      email,
      password,
    });
    
    const { token, user } = response.data;
    
    if (token) {
      setToken(token);
      // Set auth header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      return { success: true, user };
    }
    
    return { success: false, error: 'No token received' };
  } catch (error) {
    console.error('Registration error:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to register user',
    };
  }
};

// Login user
export const login = async (email, password) => {
  try {
    const response = await axios.post(`${API_URL}/login`, {
      email,
      password,
    });
    
    const { token, user } = response.data;
    
    if (token) {
      setToken(token);
      // Set auth header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      return { success: true, user };
    }
    
    return { success: false, error: 'No token received' };
  } catch (error) {
    console.error('Login error:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Invalid email or password',
    };
  }
};

// Logout user
export const logout = () => {
  removeToken();
  // Remove auth header
  delete axios.defaults.headers.common['Authorization'];
  return { success: true };
};

// Check if user is authenticated
export const checkAuth = async () => {
  const token = getToken();
  
  if (!token || !isTokenValid(token)) {
    removeToken();
    return { isAuthenticated: false, user: null };
  }
  
  // Set auth header with current token
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  
  try {
    // Get current user profile
    const response = await axios.get(`${API_URL}/profile`);
    return { isAuthenticated: true, user: response.data.user };
  } catch (error) {
    console.error('Auth check error:', error);
    removeToken();
    return { isAuthenticated: false, user: null };
  }
};

// Get user profile
export const getUserProfile = async () => {
  try {
    const response = await axios.get(`${API_URL}/profile`);
    return { success: true, user: response.data.user };
  } catch (error) {
    console.error('Get profile error:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to fetch user profile',
    };
  }
};

// Update user profile
export const updateUserProfile = async (userData) => {
  try {
    const response = await axios.put(`${API_URL}/profile`, userData);
    return { success: true, user: response.data.user };
  } catch (error) {
    console.error('Update profile error:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to update user profile',
    };
  }
}; 