import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import axios from 'axios';
import './App.css';

// Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LandingPage from './pages/LandingPage';
import Properties from './pages/Properties';
import Services from './pages/Services';
import Dashboard from './pages/Dashboard';
import PropertyDetails from './pages/PropertyDetails';
import PropertyForm from './pages/PropertyForm';
import PropertyEditForm from './pages/PropertyEditForm';
import ServiceDetails from './pages/ServiceDetails';
import BookingPage from './pages/BookingPage';
import Messages from './pages/Messages';
import Profile from './pages/Profile';

// Content Pages
import About from './pages/About';
import Contact from './pages/Contact';
import FAQ from './pages/FAQ';
import Privacy from './pages/Privacy';
import Terms from './pages/Terms';
import HelpCenter from './pages/HelpCenter';

// New Auth Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import RoleSelectionPage from './pages/auth/RoleSelectionPage';
import VerifyEmailPage from './pages/auth/VerifyEmailPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';

// Context
import { AuthProvider, useAuth } from './context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Configure axios defaults
axios.defaults.withCredentials = true;

// Protected Route Component
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/auth/login" replace />;
  }
  
  // Redirect to role selection if user doesn't have a role
  if (!user.role && window.location.pathname !== '/choose-role') {
    return <Navigate to="/choose-role" replace />;
  }
  
  return children;
}

// Public Route (redirects if authenticated)
function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
}

// Main App Component
function AppContent() {
  const { user } = useAuth();
  
  return (
    <div className="App">
      <Navbar />
      <Routes>
        {/* Public Routes */}
        <Route 
          path="/" 
          element={
            <PublicRoute>
              <LandingPage />
            </PublicRoute>
          } 
        />
        
        {/* Auth Routes */}
        <Route path="/auth/login" element={<LoginPage />} />
        <Route path="/auth/register" element={<RegisterPage />} />
        <Route path="/auth/verify-email" element={<VerifyEmailPage />} />
        <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/auth/reset-password" element={<ResetPasswordPage />} />
        
        {/* Role Selection (Protected but allows users without roles) */}
        <Route 
          path="/choose-role" 
          element={
            <ProtectedRoute>
              <RoleSelectionPage />
            </ProtectedRoute>
          } 
        />
        
        {/* Property browsing - available to all */}
        <Route path="/properties" element={<Properties />} />
        <Route path="/properties/new" element={<PropertyForm />} />
        <Route path="/properties/edit/:id" element={<PropertyEditForm />} />
        <Route path="/properties/:id" element={<PropertyDetails />} />
        <Route path="/services" element={<Services />} />
        <Route path="/services/:id" element={<ServiceDetails />} />
        
        {/* Static Content Pages - available to all */}
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/faq" element={<FAQ />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="/help-center" element={<HelpCenter />} />
        
        {/* Protected Routes */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/booking/:type/:id" 
          element={
            <ProtectedRoute>
              <BookingPage />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/messages" 
          element={
            <ProtectedRoute>
              <Messages />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } 
        />
        
        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <HelmetProvider>
      <Router>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </Router>
    </HelmetProvider>
  );
}

export default App;