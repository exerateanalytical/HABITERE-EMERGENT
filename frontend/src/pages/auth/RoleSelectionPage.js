import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Briefcase, Home, Wrench, HardHat, AlertCircle } from 'lucide-react';

const ROLES = [
  { id: 'property_seeker', name: 'Property Seeker', icon: Home, description: 'Looking for properties to buy or rent' },
  { id: 'property_owner', name: 'Property Owner', icon: Briefcase, description: 'List and manage your properties' },
  { id: 'real_estate_agent', name: 'House Agent', icon: Briefcase, description: 'Real estate professional' },
  { id: 'plumber', name: 'Plumber', icon: Wrench, description: 'Plumbing services' },
  { id: 'electrician', name: 'Electrician', icon: Wrench, description: 'Electrical services' },
  { id: 'bricklayer', name: 'Bricklayer', icon: HardHat, description: 'Construction services' },
  { id: 'carpenter', name: 'Carpenter', icon: HardHat, description: 'Carpentry services' },
  { id: 'painter', name: 'Painter', icon: HardHat, description: 'Painting services' },
];

const RoleSelectionPage = () => {
  const navigate = useNavigate();
  const { selectRole } = useAuth();
  const [selectedRole, setSelectedRole] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!selectedRole) {
      setError('Please select a role');
      return;
    }

    setLoading(true);
    setError('');

    const result = await selectRole(selectedRole);
    
    if (result.success) {
      // Redirect based on selected role
      if (selectedRole === 'property_seeker') {
        navigate('/properties');
      } else {
        navigate('/dashboard');
      }
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center px-4 py-8">
      <div className="max-w-4xl w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to Habitere!</h1>
            <p className="text-gray-600">Please tell us what best describes you</p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {ROLES.map((role) => {
              const Icon = role.icon;
              return (
                <button
                  key={role.id}
                  onClick={() => setSelectedRole(role.id)}
                  className={`p-6 rounded-xl border-2 transition-all text-left ${
                    selectedRole === role.id
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start">
                    <div className={`p-3 rounded-lg ${
                      selectedRole === role.id ? 'bg-blue-600' : 'bg-gray-100'
                    }`}>
                      <Icon className={`w-6 h-6 ${
                        selectedRole === role.id ? 'text-white' : 'text-gray-600'
                      }`} />
                    </div>
                    <div className="ml-4 flex-1">
                      <h3 className="font-semibold text-gray-900 mb-1">{role.name}</h3>
                      <p className="text-sm text-gray-600">{role.description}</p>
                    </div>
                    {selectedRole === role.id && (
                      <div className="ml-2">
                        <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      </div>
                    )}
                  </div>
                </button>
              );
            })}
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading || !selectedRole}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Saving...' : 'Continue'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default RoleSelectionPage;