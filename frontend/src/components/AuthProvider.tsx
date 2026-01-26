'use client';

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// Get API URL from environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Define types
type User = {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
};

type AuthState = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
};

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: User }
  | { type: 'LOGIN_FAILURE' }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean };

// Create context - exported for useAuth hook
export const AuthContext = createContext<{
  state: AuthState;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (email: string, password: string, confirmPassword: string) => Promise<void>;
} | undefined>(undefined);

// Reducer function
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        isLoading: true,
      };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
      };
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    default:
      return state;
  }
};

// AuthProvider component
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    isAuthenticated: false,
    isLoading: true, // Always start with loading to prevent flash
  });

  const router = useRouter();

  // Check for existing session on mount
  useEffect(() => {
    const checkSession = async () => {
      try {
        // Get token from localStorage
        const token = localStorage.getItem('access_token');

        if (!token) {
          dispatch({ type: 'LOGIN_FAILURE' });
          return;
        }

        // Verify session with Authorization header
        const response = await fetch(`${API_URL}/api/v1/auth/session`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          dispatch({ type: 'LOGIN_SUCCESS', payload: userData });
        } else {
          // Token invalid, clear localStorage
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          dispatch({ type: 'LOGIN_FAILURE' });
        }
      } catch (error) {
        console.error('Session check failed:', error);
        dispatch({ type: 'LOGIN_FAILURE' });
      } finally {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    // Only run on client side
    if (typeof window !== 'undefined') {
      checkSession();
    }
  }, []);

  // Login function
  const login = async (email: string, password: string) => {
    dispatch({ type: 'LOGIN_START' });

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
        credentials: 'include',
      });

      if (response.ok) {
        const result = await response.json();

        // Store tokens in localStorage for cross-origin auth
        if (result.access_token) {
          localStorage.setItem('access_token', result.access_token);
        }
        if (result.refresh_token) {
          localStorage.setItem('refresh_token', result.refresh_token);
        }

        // Fetch user data with the new token
        const userResponse = await fetch(`${API_URL}/api/v1/auth/session`, {
          headers: {
            'Authorization': `Bearer ${result.access_token}`,
          },
        });

        if (userResponse.ok) {
          const userData = await userResponse.json();
          dispatch({ type: 'LOGIN_SUCCESS', payload: userData });
          router.push('/tasks');
        } else {
          dispatch({ type: 'LOGIN_SUCCESS', payload: { id: 'temp', email, created_at: new Date().toISOString(), updated_at: new Date().toISOString() } });
          router.push('/tasks');
        }
      } else {
        const errorData = await response.json();
        dispatch({ type: 'LOGIN_FAILURE' });
        throw new Error(errorData.detail || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      dispatch({ type: 'LOGIN_FAILURE' });
      throw error;
    }
  };

  // Logout function
  const logout = async () => {
    try {
      const token = localStorage.getItem('access_token');
      await fetch(`${API_URL}/api/v1/auth/logout`, {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clear localStorage and state
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      dispatch({ type: 'LOGOUT' });
      router.push('/login');
    }
  };

  // Register function
  const register = async (email: string, password: string, confirmPassword: string) => {
    dispatch({ type: 'LOGIN_START' });

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, password_confirm: confirmPassword }),
        credentials: 'include', // Include cookies in the request
      });

      if (response.ok) {
        const result = await response.json();
        // After successful registration, redirect to login
        router.push('/login');
        dispatch({ type: 'LOGIN_SUCCESS', payload: { id: 'temp', email, created_at: new Date().toISOString(), updated_at: new Date().toISOString() } });
      } else {
        const errorData = await response.json();
        dispatch({ type: 'LOGIN_FAILURE' });
        throw new Error(errorData.detail || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      dispatch({ type: 'LOGIN_FAILURE' });
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ state, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
};

