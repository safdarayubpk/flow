/**
 * Authentication utilities for handling JWT tokens and user sessions.
 * This follows ADR-001 for secure JWT token storage using httpOnly cookies.
 */

// Get API URL from environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Function to get JWT token from httpOnly cookie
export const getAccessToken = (): string | null => {
  // Since we're storing tokens in httpOnly cookies, we can't access them directly from JavaScript
  // Instead, the backend will handle token validation via the cookies
  // This function is kept for potential future use if we need to handle other auth methods
  return null;
};

// Function to check if user is authenticated
export const isAuthenticated = (): boolean => {
  // Check if we have an active session by making a request to the backend
  // The backend will validate the httpOnly cookie for us
  return typeof window !== 'undefined' && !!localStorage.getItem('user_authenticated');
};

// Function to store authentication state
export const setAuthenticated = (authenticated: boolean): void => {
  if (typeof window !== 'undefined') {
    if (authenticated) {
      localStorage.setItem('user_authenticated', 'true');
    } else {
      localStorage.removeItem('user_authenticated');
    }
  }
};

// Function to clear authentication state
export const clearAuth = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('user_authenticated');
  }
};

// Function to get user info from local storage
export const getUserInfo = (): any => {
  if (typeof window !== 'undefined') {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
  }
  return null;
};

// Function to set user info in local storage
export const setUserInfo = (userInfo: any): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('user_info', JSON.stringify(userInfo));
  }
};

// Function to clear user info from local storage
export const clearUserInfo = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('user_info');
  }
};

// Function to handle API calls with authentication
export const apiCall = async (url: string, options: RequestInit = {}): Promise<Response> => {
  // Get token from localStorage
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  // Build headers with Authorization
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  };

  // Add Authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const defaultOptions: RequestInit = {
    ...options,
    headers,
    credentials: 'include', // Also include cookies as fallback
  };

  // Make the API call with the backend URL
  const fullUrl = url.startsWith('http') ? url : `${API_URL}${url}`;
  const response = await fetch(fullUrl, defaultOptions);

  // Handle authentication errors
  if (response.status === 401) {
    // User is not authenticated, clear auth state
    clearAuth();
    clearUserInfo();
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    // Optionally redirect to login page
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  return response;
};