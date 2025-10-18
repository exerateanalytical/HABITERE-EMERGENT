import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Shield, MapPin, Award, Search, Filter } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const SecurityGuards = () => {
  const navigate = useNavigate();
  const [guards, setGuards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    location: '',
    availability: ''
  });

  useEffect(() => {
    fetchGuards();
  }, [filters]);

  const fetchGuards = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.location) params.append('location', filters.location);
      if (filters.availability) params.append('availability', filters.availability);
      
      const response = await axios.get(`${BACKEND_URL}/api/security/guards/profiles?${params}`);
      setGuards(response.data);
    } catch (error) {
      console.error('Error fetching guards:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">Verified Security Guards</h1>
          <p className="text-gray-600">Browse and hire professional security personnel</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Search Location</label>
              <div className="relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="City or region"
                  className="w-full pl-10 pr-4 py-2 border rounded-lg"
                  value={filters.location}
                  onChange={(e) => setFilters({ ...filters, location: e.target.value })}
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Availability</label>
              <select
                className="w-full px-4 py-2 border rounded-lg"
                value={filters.availability}
                onChange={(e) => setFilters({ ...filters, availability: e.target.value })}
              >
                <option value="">All</option>
                <option value="Full-time">Full-time</option>
                <option value="Part-time">Part-time</option>
                <option value="On-demand">On-demand</option>
              </select>
            </div>
            
            <div className="flex items-end">
              <button
                onClick={() => setFilters({ location: '', availability: '' })}
                className="w-full bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg font-medium"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Guards Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading guards...</p>
          </div>
        ) : guards.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold mb-2">No guards found</h3>
            <p className="text-gray-600 mb-6">Try adjusting your filters or check back later</p>
            <button
              onClick={() => setFilters({ location: '', availability: '' })}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
            >
              Clear Filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {guards.map((guard) => (
              <div
                key={guard.id}
                onClick={() => navigate(`/security/guards/${guard.id}`)}
                className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow cursor-pointer"
              >
                <div className="h-48 bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
                  {guard.photo_url ? (
                    <img src={guard.photo_url} alt={guard.full_name} className="w-full h-full object-cover" />
                  ) : (
                    <Shield className="w-20 h-20 text-white" />
                  )}
                </div>
                
                <div className="p-6">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-xl font-bold">{guard.full_name}</h3>
                    {guard.verified && (
                      <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Verified</span>
                    )}
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-500 mb-3">
                    <MapPin className="w-4 h-4 mr-1" />
                    <span>{guard.city}</span>
                  </div>
                  
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <div className="text-sm text-gray-600">Experience</div>
                      <div className="font-bold text-green-600">{guard.experience_years} years</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Availability</div>
                      <div className="font-bold text-sm">{guard.availability}</div>
                    </div>
                  </div>
                  
                  {guard.certifications && guard.certifications.length > 0 && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Award className="w-4 h-4 mr-1" />
                      <span>{guard.certifications.length} Certifications</span>
                    </div>
                  )}
                  
                  <button className="w-full mt-4 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700">
                    View Profile
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SecurityGuards;