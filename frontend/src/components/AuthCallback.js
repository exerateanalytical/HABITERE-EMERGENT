import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const USER_ROLES = [
  { value: 'property_seeker', label: 'Property Seeker', description: 'Looking to rent or buy properties' },
  { value: 'property_owner', label: 'Property Owner', description: 'List properties for rent or sale' },
  { value: 'real_estate_agent', label: 'Real Estate Agent', description: 'Professional real estate services' },
  { value: 'real_estate_company', label: 'Real Estate Company', description: 'Real estate business' },
  { value: 'construction_company', label: 'Construction Company', description: 'Construction and building services' },
  { value: 'bricklayer', label: 'Bricklayer', description: 'Masonry and bricklaying services' },
  { value: 'plumber', label: 'Plumber', description: 'Plumbing installation and repair' },
  { value: 'electrician', label: 'Electrician', description: 'Electrical installation and repair' },
  { value: 'interior_designer', label: 'Interior Designer', description: 'Interior design services' },
  { value: 'borehole_driller', label: 'Borehole Driller', description: 'Water well drilling services' },
  { value: 'cleaning_company', label: 'Cleaning Company', description: 'Professional cleaning services' },
  { value: 'painter', label: 'Painter', description: 'Interior and exterior painting' },
  { value: 'architect', label: 'Architect', description: 'Architectural design services' },
  { value: 'carpenter', label: 'Carpenter', description: 'Carpentry and woodwork services' },
  { value: 'evaluator', label: 'Property Evaluator', description: 'Property valuation services' },
  { value: 'building_material_supplier', label: 'Building Material Supplier', description: 'Construction materials supply' },
  { value: 'furnishing_shop', label: 'Furnishing Shop', description: 'Home furnishing and furniture' }
];

const AuthCallback = () => {
  const [loading, setLoading] = useState(true);
  const [showRoleSelection, setShowRoleSelection] = useState(false);
  const [selectedRole, setSelectedRole] = useState('');
  const [userData, setUserData] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { completeAuth } = useAuth();

  useEffect(() => {
    processAuth();
  }, []);

  const processAuth = async () => {
    try {
      // Get session_id from URL fragment
      const fragment = window.location.hash.substring(1);
      const params = new URLSearchParams(fragment);
      const sessionId = params.get('session_id');

      if (!sessionId) {
        setError('No session ID found in URL');
        setLoading(false);
        return;
      }

      // Get session data from emergent auth
      const response = await axios.get(`${API}/auth/session-data`, {
        headers: {
          'X-Session-ID': sessionId
        }
      });

      if (response.data) {
        setUserData(response.data);
        setShowRoleSelection(true);
      } else {
        setError('Failed to get session data');
      }
    } catch (error) {
      console.error('Auth processing error:', error);
      setError(error.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedRole) {
      setError('Please select a role');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const success = await completeAuth(userData, selectedRole);
      
      if (success) {
        // Clear URL fragment
        window.history.replaceState({}, document.title, window.location.pathname);
        navigate('/dashboard');
      } else {
        setError('Failed to complete authentication');
      }
    } catch (error) {
      console.error('Role submission error:', error);
      setError('Failed to complete authentication');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50" data-testid="auth-loading">
        <div className="max-w-md w-full space-y-8 text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-gray-900">Completing Authentication</h2>
            <p className="text-gray-600">Please wait while we set up your account...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50" data-testid="auth-error">
        <div className="max-w-md w-full space-y-8 text-center">
          <div className="bg-red-50 border border-red-200 rounded-xl p-6">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-red-900 mb-2">Authentication Failed</h2>
            <p className="text-red-700">{error}</p>
            <button
              onClick={() => navigate('/')}
              className="mt-4 btn-primary"
            >
              Return to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (showRoleSelection) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 mb-4">
              <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900">Welcome to Habitere!</h2>
            <p className="mt-2 text-gray-600">
              Hello {userData?.name}! Please select your role to complete your profile.
            </p>
          </div>

          <form onSubmit={handleRoleSubmit} className="bg-white shadow-xl rounded-xl p-8" data-testid="role-selection-form">
            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Choose your role on Habitere:
              </label>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
                {USER_ROLES.map((role) => (
                  <label 
                    key={role.value}
                    className={`relative flex items-start p-4 border-2 rounded-lg cursor-pointer hover:bg-blue-50 transition-colors ${
                      selectedRole === role.value ? 'border-blue-600 bg-blue-50' : 'border-gray-200'
                    }`}
                  >
                    <input
                      type="radio"
                      name="role"
                      value={role.value}
                      checked={selectedRole === role.value}
                      onChange={(e) => setSelectedRole(e.target.value)}
                      className="sr-only"
                      data-testid={`role-${role.value}`}
                    />
                    <div className="flex-1 min-w-0">
                      <h3 className={`text-sm font-medium ${
                        selectedRole === role.value ? 'text-blue-900' : 'text-gray-900'
                      }`}>
                        {role.label}
                      </h3>
                      <p className={`text-xs ${
                        selectedRole === role.value ? 'text-blue-700' : 'text-gray-500'
                      }`}>
                        {role.description}
                      </p>
                    </div>
                    {selectedRole === role.value && (
                      <div className="flex-shrink-0">
                        <svg className="h-5 w-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </label>
                ))}
              </div>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <div className="mt-8 flex justify-center">
              <button
                type="submit"
                disabled={!selectedRole || loading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="complete-registration-btn"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Completing Registration...
                  </>
                ) : (
                  'Complete Registration'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return null;
};

export default AuthCallback;