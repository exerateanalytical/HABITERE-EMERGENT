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

  // Set up axios interceptor to handle 401 errors
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      response => response,
      error => {
        if (error.response?.status === 401 && error.config.url !== `${API}/auth/me`) {
          console.log('Authentication failed - clearing user state');
          setUser(null);
        }
        return Promise.reject(error);
      }
    );

    return () => axios.interceptors.response.eject(interceptor);
  }, []);

  const checkExistingSession = async () => {
    console.log('[AuthContext] Checking existing session...');
    try {
      const response = await axios.get(`${API}/auth/me`, { withCredentials: true });
      console.log('[AuthContext] Session check response:', response.data);
      if (response.data) {
        setUser(response.data);
        console.log('[AuthContext] User loaded:', response.data.email, 'Role:', response.data.role);
      } else {
        setUser(null);
        console.log('[AuthContext] No user data in response');
      }
    } catch (error) {
      console.log('[AuthContext] No existing session:', error.response?.status);
      setUser(null);
    } finally {
      setLoading(false);
      console.log('[AuthContext] Session check complete');
    }
  };

  // Email/Password Registration
  const register = async (email, password, name, phone) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        email,
        password,
        name,
        phone
      }, { withCredentials: true });
      
      // Registration now returns user data and session - auto-login
      if (response.data.user) {
        setUser(response.data.user);
        console.log('[AuthContext] User registered and auto-logged in:', response.data.user.email);
      }
      
      return { 
        success: true, 
        message: response.data.message,
        user: response.data.user
      };
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed. Please try again.' 
      };
    }
  };

  // Email/Password Login
  const login = async (email, password) => {
    try {
      console.log('[AuthContext] Attempting login for:', email);
      const response = await axios.post(`${API}/auth/login`, {
        email,
        password
      }, { withCredentials: true });
      
      console.log('[AuthContext] Login response:', response.data);
      
      if (response.data.user) {
        setUser(response.data.user);
        console.log('[AuthContext] User set after login:', response.data.user.email, 'Role:', response.data.user.role);
        return { 
          success: true, 
          user: response.data.user,
          needsRoleSelection: response.data.needs_role_selection
        };
      }
      return { success: false, error: 'Login failed' };
    } catch (error) {
      console.error('[AuthContext] Login error:', error.response?.data);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed. Please try again.' 
      };
    }
  };

  // Google OAuth Login
  const loginWithGoogle = async () => {
    try {
      const response = await axios.get(`${API}/auth/google/login`);
      if (response.data.auth_url) {
        window.location.href = response.data.auth_url;
      }
    } catch (error) {
      console.error('Google login error:', error);
      return { 
        success: false, 
        error: 'Failed to initiate Google login' 
      };
    }
  };

  // Email Verification
  const verifyEmail = async (token) => {
    try {
      const response = await axios.post(`${API}/auth/verify-email`, {
        token
      }, { withCredentials: true });
      
      if (response.data.user) {
        setUser(response.data.user);
        return { 
          success: true, 
          message: response.data.message,
          needsRoleSelection: response.data.needs_role_selection
        };
      }
      return { success: true, message: response.data.message };
    } catch (error) {
      console.error('Email verification error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Verification failed' 
      };
    }
  };

  // Resend Verification Email
  const resendVerification = async (email) => {
    try {
      const response = await axios.post(`${API}/auth/resend-verification`, {
        email
      });
      return { success: true, message: response.data.message };
    } catch (error) {
      console.error('Resend verification error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to resend verification email' 
      };
    }
  };

  // Forgot Password
  const forgotPassword = async (email) => {
    try {
      const response = await axios.post(`${API}/auth/forgot-password`, {
        email
      });
      return { success: true, message: response.data.message };
    } catch (error) {
      console.error('Forgot password error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to send reset email' 
      };
    }
  };

  // Reset Password
  const resetPassword = async (token, newPassword) => {
    try {
      const response = await axios.post(`${API}/auth/reset-password`, {
        token,
        new_password: newPassword
      });
      return { success: true, message: response.data.message };
    } catch (error) {
      console.error('Reset password error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to reset password' 
      };
    }
  };

  // Select Role
  const selectRole = async (role) => {
    try {
      const response = await axios.post(`${API}/auth/select-role`, {
        role
      }, { withCredentials: true });
      
      if (response.data.user) {
        setUser(response.data.user);
        return { success: true, user: response.data.user };
      }
      return { success: false, error: 'Failed to select role' };
    } catch (error) {
      console.error('Role selection error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to select role' 
      };
    }
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
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
    loginWithGoogle,
    verifyEmail,
    resendVerification,
    forgotPassword,
    resetPassword,
    selectRole,
    logout,
    checkExistingSession
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};