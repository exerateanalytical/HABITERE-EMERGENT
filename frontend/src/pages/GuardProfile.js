import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Shield, MapPin, Star, Phone, Mail, CheckCircle, Award, Calendar, Briefcase, ArrowLeft } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const GuardProfile = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [guard, setGuard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGuardProfile();
  }, [id]);

  const fetchGuardProfile = async () => {
    try {
      // Fetch from guard applications (approved guards)
      const response = await axios.get(`${BACKEND_URL}/api/security/guards/profiles`);
      const foundGuard = response.data.find(g => g.id === id);
      
      if (foundGuard) {
        setGuard(foundGuard);
      } else {
        alert('Guard profile not found');
        navigate('/security/guards');
      }
    } catch (error) {
      console.error('Error fetching guard profile:', error);
      alert('Failed to load guard profile');
      navigate('/security/guards');
    } finally {
      setLoading(false);
    }
  };

  const calculateAge = (dob) => {
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (!guard) return null;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-5xl">
        {/* Back Button */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center text-gray-600 hover:text-green-600 mb-6"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Profile */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-8">
              {/* Header */}
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center">
                  <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mr-4">
                    {guard.photo_url ? (
                      <img src={guard.photo_url} alt={guard.full_name} className="w-24 h-24 rounded-full object-cover" />
                    ) : (
                      <Shield className="w-12 h-12 text-green-600" />
                    )}
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold mb-1">{guard.full_name}</h1>
                    <p className="text-gray-600">Professional Security Guard</p>
                    <div className="flex items-center mt-2">
                      <MapPin className="w-4 h-4 text-gray-500 mr-1" />
                      <span className="text-sm text-gray-600">{guard.city}</span>
                    </div>
                  </div>
                </div>
                {guard.verified && (
                  <div className="flex items-center bg-green-100 text-green-800 px-3 py-2 rounded-lg">
                    <CheckCircle className="w-5 h-5 mr-2" />
                    <span className="font-semibold">Verified</span>
                  </div>
                )}
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-4 mb-6 pb-6 border-b">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{guard.experience_years}</div>
                  <div className="text-sm text-gray-600">Years Experience</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{guard.certifications?.length || 0}</div>
                  <div className="text-sm text-gray-600">Certifications</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{guard.preferred_locations?.length || 0}</div>
                  <div className="text-sm text-gray-600">Locations</div>
                </div>
              </div>

              {/* Bio */}
              {guard.bio && (
                <div className="mb-6">
                  <h2 className="text-xl font-bold mb-3">About</h2>
                  <p className="text-gray-700 leading-relaxed">{guard.bio}</p>
                </div>
              )}

              {/* Experience */}
              <div className="mb-6">
                <h2 className="text-xl font-bold mb-3 flex items-center">
                  <Briefcase className="w-5 h-5 mr-2 text-green-600" />
                  Professional Experience
                </h2>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <Calendar className="w-4 h-4 text-gray-500 mr-2" />
                    <span className="font-semibold">{guard.experience_years} years in security services</span>
                  </div>
                  {guard.previous_employers && guard.previous_employers.length > 0 && (
                    <div className="mt-3">
                      <div className="text-sm text-gray-600 mb-2">Previous Employers:</div>
                      <div className="flex flex-wrap gap-2">
                        {guard.previous_employers.map((employer, index) => (
                          <span key={index} className="bg-white px-3 py-1 rounded-full text-sm border">
                            {employer}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Certifications */}
              {guard.certifications && guard.certifications.length > 0 && (
                <div className="mb-6">
                  <h2 className="text-xl font-bold mb-3 flex items-center">
                    <Award className="w-5 h-5 mr-2 text-green-600" />
                    Certifications & Licenses
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {guard.certifications.map((cert, index) => (
                      <div key={index} className="flex items-center bg-blue-50 px-4 py-3 rounded-lg">
                        <CheckCircle className="w-5 h-5 text-blue-600 mr-3" />
                        <span className="font-medium">{cert}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Training */}
              {guard.training && guard.training.length > 0 && (
                <div className="mb-6">
                  <h2 className="text-xl font-bold mb-3">Specialized Training</h2>
                  <div className="flex flex-wrap gap-2">
                    {guard.training.map((training, index) => (
                      <span key={index} className="bg-green-100 text-green-800 px-3 py-2 rounded-lg text-sm">
                        {training}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Preferred Locations */}
              {guard.preferred_locations && guard.preferred_locations.length > 0 && (
                <div>
                  <h2 className="text-xl font-bold mb-3">Preferred Work Locations</h2>
                  <div className="flex flex-wrap gap-2">
                    {guard.preferred_locations.map((location, index) => (
                      <span key={index} className="bg-gray-100 px-3 py-2 rounded-lg text-sm flex items-center">
                        <MapPin className="w-4 h-4 mr-1 text-gray-600" />
                        {location}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            {/* Contact Card */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6 sticky top-24">
              <h3 className="text-lg font-bold mb-4">Contact Information</h3>
              
              <div className="space-y-3 mb-6">
                <div className="flex items-center">
                  <Phone className="w-5 h-5 text-gray-500 mr-3" />
                  <span className="text-sm">{guard.phone}</span>
                </div>
                <div className="flex items-center">
                  <Mail className="w-5 h-5 text-gray-500 mr-3" />
                  <span className="text-sm break-all">{guard.email}</span>
                </div>
                <div className="flex items-center">
                  <MapPin className="w-5 h-5 text-gray-500 mr-3" />
                  <span className="text-sm">{guard.city}</span>
                </div>
              </div>

              <div className="space-y-2">
                <button
                  onClick={() => window.location.href = `mailto:${guard.email}`}
                  className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700"
                >
                  Contact Guard
                </button>
                <button
                  onClick={() => window.location.href = `tel:${guard.phone}`}
                  className="w-full bg-white border-2 border-green-600 text-green-600 py-3 rounded-lg font-semibold hover:bg-green-50"
                >
                  Call Now
                </button>
              </div>
            </div>

            {/* Availability Card */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-bold mb-4">Availability</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Status</span>
                  <span className={`font-semibold px-3 py-1 rounded-full ${
                    guard.availability === 'Full-time' ? 'bg-green-100 text-green-800' :
                    guard.availability === 'Part-time' ? 'bg-blue-100 text-blue-800' :
                    'bg-orange-100 text-orange-800'
                  }`}>
                    {guard.availability}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Age</span>
                  <span className="font-semibold">{calculateAge(guard.date_of_birth)} years</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Verified</span>
                  <span className="font-semibold text-green-600">
                    {guard.verified ? 'Yes' : 'Pending'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GuardProfile;
