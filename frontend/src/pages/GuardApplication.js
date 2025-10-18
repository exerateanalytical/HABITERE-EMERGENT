import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Shield, Upload, CheckCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const GuardApplication = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    full_name: user?.name || '',
    phone: user?.phone || '',
    email: user?.email || '',
    date_of_birth: '',
    national_id: '',
    address: '',
    city: '',
    experience_years: 0,
    previous_employers: [],
    certifications: [],
    training: [],
    availability: 'Full-time',
    preferred_locations: [],
    id_document_url: '',
    photo_url: ''
  });

  useEffect(() => {
    if (!user) {
      alert('Please login to submit a guard application');
      navigate('/auth/login');
    }
  }, [user, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!user) {
      alert('Please login to apply');
      navigate('/auth/login');
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${BACKEND_URL}/api/security/guards/apply`,
        formData,
        { withCredentials: true }
      );
      setSuccess(true);
    } catch (error) {
      console.error('Error submitting application:', error);
      alert(error.response?.data?.detail || 'Failed to submit application');
    } finally {
      setLoading(false);
    }
  };

  const handleArrayInput = (field, value) => {
    const array = value.split(',').map(item => item.trim()).filter(item => item);
    setFormData({ ...formData, [field]: array });
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4 max-w-2xl">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <CheckCircle className="w-20 h-20 text-green-600 mx-auto mb-6" />
            <h2 className="text-3xl font-bold mb-4">Application Submitted!</h2>
            <p className="text-gray-600 mb-8">
              Thank you for applying to become a security guard with Homeland Security.
              Our team will review your application and contact you within 2-3 business days.
            </p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => navigate('/security')}
                className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
              >
                Back to Security
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-3xl">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="flex items-center mb-6">
            <Shield className="w-10 h-10 text-green-600 mr-3" />
            <div>
              <h1 className="text-3xl font-bold">Apply as Security Guard</h1>
              <p className="text-gray-600">Join our professional security team</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Personal Information */}
            <div>
              <h3 className="text-xl font-bold mb-4">Personal Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Full Name *</label>
                  <input
                    type="text"
                    required
                    className="w-full px-4 py-2 border rounded-lg"
                    value={formData.full_name}
                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Phone *</label>
                  <input
                    type="tel"
                    required
                    className="w-full px-4 py-2 border rounded-lg"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Email *</label>
                  <input
                    type="email"
                    required
                    className="w-full px-4 py-2 border rounded-lg"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Date of Birth *</label>
                  <input
                    type="date"
                    required
                    className="w-full px-4 py-2 border rounded-lg"
                    value={formData.date_of_birth}
                    onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">National ID *</label>
                  <input
                    type="text"
                    required
                    className="w-full px-4 py-2 border rounded-lg"
                    value={formData.national_id}
                    onChange={(e) => setFormData({ ...formData, national_id: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">City *</label>
                  <input
                    type="text"
                    required
                    className="w-full px-4 py-2 border rounded-lg"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  />
                </div>
              </div>
              <div className="mt-4">
                <label className="block text-sm font-medium mb-2">Address *</label>
                <textarea
                  required
                  rows={3}
                  className="w-full px-4 py-2 border rounded-lg"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                />
              </div>
            </div>

            {/* Professional Information */}
            <div>
              <h3 className="text-xl font-bold mb-4">Professional Information</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Years of Experience *</label>
                  <input
                    type="number"
                    required
                    min="0"
                    className="w-full px-4 py-2 border rounded-lg"
                    value={formData.experience_years}
                    onChange={(e) => setFormData({ ...formData, experience_years: parseInt(e.target.value) })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Availability *</label>
                  <select
                    required
                    className="w-full px-4 py-2 border rounded-lg"
                    value={formData.availability}
                    onChange={(e) => setFormData({ ...formData, availability: e.target.value })}
                  >
                    <option value="Full-time">Full-time</option>
                    <option value="Part-time">Part-time</option>
                    <option value="On-demand">On-demand</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Previous Employers (comma separated)</label>
                  <input
                    type="text"
                    className="w-full px-4 py-2 border rounded-lg"
                    placeholder="Company 1, Company 2, Company 3"
                    onChange={(e) => handleArrayInput('previous_employers', e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Certifications (comma separated)</label>
                  <input
                    type="text"
                    className="w-full px-4 py-2 border rounded-lg"
                    placeholder="First Aid, Firearms Training, etc."
                    onChange={(e) => handleArrayInput('certifications', e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Training (comma separated)</label>
                  <input
                    type="text"
                    className="w-full px-4 py-2 border rounded-lg"
                    placeholder="Military, Police Academy, etc."
                    onChange={(e) => handleArrayInput('training', e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Preferred Locations (comma separated)</label>
                  <input
                    type="text"
                    className="w-full px-4 py-2 border rounded-lg"
                    placeholder="Douala, Yaounde, Buea"
                    onChange={(e) => handleArrayInput('preferred_locations', e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* Submit */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400 flex items-center justify-center"
              >
                {loading ? 'Submitting...' : 'Submit Application'}
              </button>
              <button
                type="button"
                onClick={() => navigate('/security')}
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default GuardApplication;
