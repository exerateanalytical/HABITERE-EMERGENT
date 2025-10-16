import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing session on app load
  useEffect(() => {
    checkExistingSession();
  }, []);

  const checkExistingSession = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      if (response.data) {
        setUser(response.data);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.log('No existing session found');
      setUser(null); // Clear user state if session is invalid
    } finally {
      setLoading(false);
    }
  };

  const login = (redirectUrl) => {
    const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
    window.location.href = authUrl;
  };

  const completeAuth = async (userData, role) => {
    try {
      const response = await axios.post(`${API}/auth/complete`, userData, {
        params: { role }
      });
      
      if (response.data.user) {
        setUser(response.data.user);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Authentication completion failed:', error);
      return false;
    }
  };

  const register = async (formData) => {
    try {
      const response = await axios.post(`${API}/auth/register`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if (response.data.user) {
        setUser(response.data.user);
        return { success: true, user: response.data.user };
      }
      return { success: false, error: 'Registration failed' };
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed. Please try again.' 
      };
    }
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      window.location.href = '/';
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    completeAuth,
    logout,
    checkExistingSession
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};