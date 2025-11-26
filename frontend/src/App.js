import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import axios from 'axios';
import './App.css';

// Components
import Navbar from './components/Navbar';
import Footer from './components/FooterMobile';
import BackToTop from './components/BackToTop';
import ScrollToTop from './components/ScrollToTop';
import LandingPage from './pages/LandingPage';
import Properties from './pages/Properties';
import Services from './pages/Services';
import Dashboard from './pages/Dashboard';
import PropertyDetails from './pages/PropertyDetails';
import PropertyForm from './pages/PropertyForm';
import PropertyEditForm from './pages/PropertyEditForm';
import ServiceDetails from './pages/ServiceDetails';
import ServiceProviderDashboard from './pages/ServiceProviderDashboard';
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

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUsers from './pages/admin/AdminUsers';
import AdminProperties from './pages/admin/AdminProperties';

// Homeland Security Pages
import HomelandSecurity from './pages/HomelandSecurity';
import SecurityServices from './pages/SecurityServices';
import GuardApplication from './pages/GuardApplication';
import SecurityServiceDetail from './pages/SecurityServiceDetail';
import GuardProfile from './pages/GuardProfile';
import SecurityGuards from './pages/SecurityGuards';
import SecurityBookings from './pages/SecurityBookings';
import ProviderDashboard from './pages/ProviderDashboard';
import SecurityAdmin from './pages/admin/SecurityAdmin';

// Asset Management Pages
import AssetManagementLanding from './pages/AssetManagementLanding';
import AssetDashboard from './pages/AssetDashboard';
import AssetsList from './pages/AssetsList';
import AssetForm from './pages/AssetForm';
import AssetDetail from './pages/AssetDetail';
import MaintenanceList from './pages/MaintenanceList';
import MaintenanceForm from './pages/MaintenanceForm';
import MaintenanceDetail from './pages/MaintenanceDetail';
import ExpensesList from './pages/ExpensesList';
import InventoryList from './pages/InventoryList';
import InventoryForm from './pages/InventoryForm';
import InventoryDetail from './pages/InventoryDetail';

// House Plans Module
import HousePlanBuilder from './pages/HousePlanBuilder';
import MyHousePlans from './pages/MyHousePlans';
import HousePlanDetail from './pages/HousePlanDetail';

// New Auth Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import RoleSelectionPage from './pages/auth/RoleSelectionPage';
import VerifyEmailPage from './pages/auth/VerifyEmailPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';

// Subscription Pages
import PricingPage from './pages/PricingPage';
import CheckoutPage from './pages/CheckoutPage';
import SubscriptionDashboard from './pages/SubscriptionDashboard';

// Context
import { AuthProvider, useAuth } from './context/AuthContext';
import { LocationProvider } from './context/LocationContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Configure axios defaults
axios.defaults.withCredentials = true;

// Protected Route Component
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  
  console.log('[ProtectedRoute] Loading:', loading, 'User:', user);
  
  if (loading) {
    console.log('[ProtectedRoute] Still loading, showing spinner');
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (!user) {
    console.log('[ProtectedRoute] No user found, redirecting to /auth/login');
    return <Navigate to="/auth/login" replace />;
  }
  
  // Redirect to role selection if user doesn't have a role
  if (!user.role && window.location.pathname !== '/choose-role') {
    console.log('[ProtectedRoute] User has no role, redirecting to /choose-role');
    return <Navigate to="/choose-role" replace />;
  }
  
  console.log('[ProtectedRoute] User authenticated, rendering protected content');
  return children;
}

// Admin Route Component - Only for admin users
function AdminRoute({ children }) {
  const { user, loading } = useAuth();
  
  console.log('[AdminRoute] Loading:', loading, 'User:', user);
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin panel...</p>
        </div>
      </div>
    );
  }
  
  console.log('[AdminRoute] User authenticated:', !!user, 'Role:', user?.role);
  
  if (!user) {
    console.log('[AdminRoute] No user - redirecting to login');
    return <Navigate to="/auth/login" replace state={{ from: '/admin' }} />;
  }
  
  // Check if user is admin
  if (user.role !== 'admin') {
    console.log('[AdminRoute] User is not admin - showing access denied');
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-4">You do not have permission to access the admin panel.</p>
          <p className="text-sm text-gray-500 mb-6">Your role: <span className="font-semibold">{user.role || 'None'}</span></p>
          <button
            onClick={() => window.location.href = '/'}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Return to Home
          </button>
        </div>
      </div>
    );
  }
  
  console.log('[AdminRoute] Access granted - rendering admin content');
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
        {/* Most specific routes first to prevent wildcard matching */}
        <Route 
          path="/properties/new" 
          element={
            <ProtectedRoute>
              <PropertyForm />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/properties/edit/:id" 
          element={
            <ProtectedRoute>
              <PropertyEditForm />
            </ProtectedRoute>
          } 
        />
        <Route path="/properties/:id" element={<PropertyDetails />} />
        <Route path="/properties" element={<Properties />} />
        <Route path="/services" element={<Services />} />
        <Route path="/services/:id" element={<ServiceDetails />} />
        <Route 
          path="/provider/services" 
          element={
            <ProtectedRoute>
              <ServiceProviderDashboard />
            </ProtectedRoute>
          } 
        />
        
        {/* Static Content Pages - available to all */}
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/faq" element={<FAQ />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="/help-center" element={<HelpCenter />} />
        
        {/* Subscription & Pricing */}
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/checkout" element={<CheckoutPage />} />
        <Route 
          path="/subscription" 
          element={
            <ProtectedRoute>
              <SubscriptionDashboard />
            </ProtectedRoute>
          } 
        />
        
        {/* Homeland Security Routes */}
        <Route path="/security" element={<HomelandSecurity />} />
        <Route path="/security/services" element={<SecurityServices />} />
        <Route path="/security/services/:id" element={<SecurityServiceDetail />} />
        <Route path="/security/guards" element={<SecurityGuards />} />
        <Route path="/security/guards/:id" element={<GuardProfile />} />
        <Route path="/security/bookings" element={<SecurityBookings />} />
        <Route path="/security/apply" element={<GuardApplication />} />
        <Route path="/provider/dashboard" element={<ProviderDashboard />} />
        <Route path="/admin/security" element={<SecurityAdmin />} />
        
        {/* Asset Management Landing Page - Public */}
        <Route path="/assets" element={<AssetManagementLanding />} />
        
        {/* Asset Management Routes - Protected */}
        <Route 
          path="/assets/dashboard" 
          element={
            <ProtectedRoute>
              <AssetDashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/assets/list" 
          element={
            <ProtectedRoute>
              <AssetsList />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/assets/create" 
          element={
            <ProtectedRoute>
              <AssetForm mode="create" />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/assets/:assetId" 
          element={
            <ProtectedRoute>
              <AssetDetail />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/assets/:assetId/edit" 
          element={
            <ProtectedRoute>
              <AssetForm mode="edit" />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/assets/maintenance" 
          element={
            <ProtectedRoute>
              <MaintenanceList />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/assets/maintenance/create" 
          element={
            <ProtectedRoute>
              <MaintenanceForm />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/assets/maintenance/:taskId" 
          element={
            <ProtectedRoute>
              <MaintenanceDetail />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/assets/expenses" 
          element={
            <ProtectedRoute>
              <ExpensesList />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/assets/inventory" 
          element={
            <ProtectedRoute>
              <InventoryList />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/assets/inventory/create" 
          element={
            <ProtectedRoute>
              <InventoryForm mode="create" />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/assets/inventory/:itemId" 
          element={
            <ProtectedRoute>
              <InventoryDetail />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/assets/inventory/:itemId/edit" 
          element={
            <ProtectedRoute>
              <InventoryForm mode="edit" />
            </ProtectedRoute>
          } 
        />

        {/* House Plans Module Routes */}
        <Route 
          path="/house-plans/builder" 
          element={
            <ProtectedRoute>
              <HousePlanBuilder />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/house-plans/my-plans" 
          element={
            <ProtectedRoute>
              <MyHousePlans />
            </ProtectedRoute>
          } 
        />
        
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
        
        {/* Admin Routes */}
        <Route 
          path="/admin" 
          element={
            <AdminRoute>
              <AdminDashboard />
            </AdminRoute>
          } 
        />
        
        <Route 
          path="/admin/users" 
          element={
            <AdminRoute>
              <AdminUsers />
            </AdminRoute>
          } 
        />
        
        <Route 
          path="/admin/properties" 
          element={
            <AdminRoute>
              <AdminProperties />
            </AdminRoute>
          } 
        />
        
        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Footer />
      <BackToTop />
    </div>
  );
}

function App() {
  return (
    <HelmetProvider>
      <Router>
        <ScrollToTop />
        <AuthProvider>
          <LocationProvider>
            <AppContent />
          </LocationProvider>
        </AuthProvider>
      </Router>
    </HelmetProvider>
  );
}

export default App;