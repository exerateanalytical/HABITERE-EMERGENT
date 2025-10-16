import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Building, 
  Edit3, 
  Camera,
  Save,
  X,
  Shield,
  Award,
  Calendar,
  Home,
  Eye,
  Heart,
  Plus
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Helper function to get proper image URL
const getImageUrl = (url) => {
  if (!url) return 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400';
  return url.startsWith('/uploads/') ? `${BACKEND_URL}${url}` : url;
};

const Profile = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [myProperties, setMyProperties] = useState([]);
  const [myServices, setMyServices] = useState([]);
  const [loadingProperties, setLoadingProperties] = useState(false);
  const [editData, setEditData] = useState({
    name: user?.name || '',
    phone: user?.phone || '',
    location: user?.location || '',
    company_name: user?.company_name || '',
    bio: user?.bio || ''
  });

  useEffect(() => {
    if (user) {
      fetchMyProperties();
      fetchMyServices();
    }
  }, [user]);

  const fetchMyProperties = async () => {
    try {
      setLoadingProperties(true);
      const response = await axios.get(`${API}/properties`);
      console.log('All properties:', response.data);
      console.log('Current user ID:', user?.id);
      console.log('Current user email:', user?.email);
      
      // Filter properties owned by current user
      const userProperties = response.data.filter(prop => {
        console.log(`Checking property: ${prop.title}, owner_id: ${prop.owner_id}`);
        return prop.owner_id === user?.id;
      });
      
      console.log('User properties found:', userProperties.length);
      setMyProperties(userProperties);
    } catch (error) {
      console.error('Error fetching properties:', error);
    } finally {
      setLoadingProperties(false);
    }
  };

  const fetchMyServices = async () => {
    try {
      const response = await axios.get(`${API}/services`);
      // Filter services owned by current user
      const userServices = response.data.filter(service => service.provider_id === user?.id);
      setMyServices(userServices);
    } catch (error) {
      console.error('Error fetching services:', error);
    }
  };

  const handleSave = async () => {
    try {
      // In a real app, this would make an API call to update the user profile
      console.log('Saving profile data:', editData);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating profile:', error);
    }
  };

  const handleCancel = () => {
    setEditData({
      name: user?.name || '',
      phone: user?.phone || '',
      location: user?.location || '',
      company_name: user?.company_name || '',
      bio: user?.bio || ''
    });
    setIsEditing(false);
  };

  const handleInputChange = (field, value) => {
    setEditData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getRoleDisplayName = (role) => {
    return role?.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ') || '';
  };

  const getRoleColor = (role) => {
    const colorMap = {
      'property_seeker': 'bg-blue-100 text-blue-800',
      'property_owner': 'bg-green-100 text-green-800',
      'real_estate_agent': 'bg-purple-100 text-purple-800',
      'real_estate_company': 'bg-indigo-100 text-indigo-800',
      'construction_company': 'bg-orange-100 text-orange-800',
      'admin': 'bg-red-100 text-red-800'
    };
    return colorMap[role] || 'bg-gray-100 text-gray-800';
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Not Authenticated</h2>
          <p className="text-gray-600">Please log in to view your profile.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="profile-page">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl p-6 sm:p-8 mb-6 sm:mb-8 text-white">
          <div className="flex flex-col md:flex-row items-center space-y-4 md:space-y-0 md:space-x-6">
            <div className="relative">
              <div className="w-32 h-32 bg-white bg-opacity-20 rounded-full flex items-center justify-center overflow-hidden">
                {user.picture ? (
                  <img 
                    src={user.picture} 
                    alt={user.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <User className="w-16 h-16 text-white" />
                )}
              </div>
              <button className="absolute bottom-2 right-2 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center hover:bg-blue-700 transition-colors">
                <Camera className="w-4 h-4 text-white" />
              </button>
            </div>
            
            <div className="text-center md:text-left flex-1">
              <h1 className="text-3xl font-bold mb-2">{user.name}</h1>
              <div className="flex items-center justify-center md:justify-start space-x-2 mb-3">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getRoleColor(user.role)}`}>
                  {getRoleDisplayName(user.role)}
                </span>
                {user.is_verified && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                    <Shield className="w-4 h-4 mr-1" />
                    Verified
                  </span>
                )}
              </div>
              <p className="text-blue-100">{user.email}</p>
              <div className="flex items-center justify-center md:justify-start mt-2 text-blue-100">
                <Calendar className="w-4 h-4 mr-2" />
                <span>Member since {new Date(user.created_at || Date.now()).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</span>
              </div>
            </div>
            
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="bg-white bg-opacity-20 hover:bg-opacity-30 px-6 py-2 rounded-lg transition-colors flex items-center"
              data-testid="edit-profile-btn"
            >
              <Edit3 className="w-5 h-5 mr-2" />
              {isEditing ? 'Cancel' : 'Edit Profile'}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Information */}
          <div className="lg:col-span-2 space-y-6">
            {/* Personal Information */}
            <div className="card">
              <div className="card-header">
                <h2 className="text-xl font-semibold text-gray-900">Personal Information</h2>
              </div>
              <div className="card-body">
                {isEditing ? (
                  <form className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Full Name
                      </label>
                      <input
                        type="text"
                        value={editData.name}
                        onChange={(e) => handleInputChange('name', e.target.value)}
                        className="form-input"
                        data-testid="edit-name"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Phone Number
                      </label>
                      <input
                        type="tel"
                        value={editData.phone}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                        placeholder="+237 6XX XX XX XX"
                        className="form-input"
                        data-testid="edit-phone"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Location
                      </label>
                      <input
                        type="text"
                        value={editData.location}
                        onChange={(e) => handleInputChange('location', e.target.value)}
                        placeholder="City, Region"
                        className="form-input"
                        data-testid="edit-location"
                      />
                    </div>

                    {user.role !== 'property_seeker' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Company Name
                        </label>
                        <input
                          type="text"
                          value={editData.company_name}
                          onChange={(e) => handleInputChange('company_name', e.target.value)}
                          placeholder="Your company or business name"
                          className="form-input"
                          data-testid="edit-company"
                        />
                      </div>
                    )}
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Bio
                      </label>
                      <textarea
                        value={editData.bio}
                        onChange={(e) => handleInputChange('bio', e.target.value)}
                        placeholder="Tell us about yourself..."
                        rows={4}
                        className="form-textarea"
                        data-testid="edit-bio"
                      />
                    </div>

                    <div className="flex justify-end space-x-3 pt-4">
                      <button
                        type="button"
                        onClick={handleCancel}
                        className="btn-secondary"
                        data-testid="cancel-edit-btn"
                      >
                        <X className="w-4 h-4 mr-2" />
                        Cancel
                      </button>
                      <button
                        type="button"
                        onClick={handleSave}
                        className="btn-primary"
                        data-testid="save-profile-btn"
                      >
                        <Save className="w-4 h-4 mr-2" />
                        Save Changes
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <Mail className="w-5 h-5 text-gray-400" />
                      <div>
                        <div className="text-sm text-gray-500">Email</div>
                        <div className="font-medium">{user.email}</div>
                      </div>
                    </div>
                    
                    {user.phone && (
                      <div className="flex items-center space-x-3">
                        <Phone className="w-5 h-5 text-gray-400" />
                        <div>
                          <div className="text-sm text-gray-500">Phone</div>
                          <div className="font-medium">{user.phone}</div>
                        </div>
                      </div>
                    )}
                    
                    {user.location && (
                      <div className="flex items-center space-x-3">
                        <MapPin className="w-5 h-5 text-gray-400" />
                        <div>
                          <div className="text-sm text-gray-500">Location</div>
                          <div className="font-medium">{user.location}</div>
                        </div>
                      </div>
                    )}
                    
                    {user.company_name && (
                      <div className="flex items-center space-x-3">
                        <Building className="w-5 h-5 text-gray-400" />
                        <div>
                          <div className="text-sm text-gray-500">Company</div>
                          <div className="font-medium">{user.company_name}</div>
                        </div>
                      </div>
                    )}
                    
                    {user.bio && (
                      <div>
                        <div className="text-sm text-gray-500 mb-2">Bio</div>
                        <div className="text-gray-700">{user.bio}</div>
                      </div>
                    )}
                    
                    {!user.phone && !user.location && !user.company_name && !user.bio && (
                      <div className="text-center py-8">
                        <User className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                        <p className="text-gray-500">Complete your profile to get better recommendations</p>
                        <button
                          onClick={() => setIsEditing(true)}
                          className="mt-2 text-blue-600 hover:text-blue-700 font-medium"
                        >
                          Add information
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Account Stats */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">Account Stats</h3>
              </div>
              <div className="card-body">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Profile Completeness</span>
                    <span className="font-semibold text-blue-600">
                      {Math.round(
                        (Object.values({
                          name: user.name,
                          email: user.email,
                          phone: user.phone,
                          location: user.location,
                          bio: user.bio
                        }).filter(Boolean).length / 5) * 100
                      )}%
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Properties Listed</span>
                    <span className="font-semibold">{myProperties.length}</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Services Offered</span>
                    <span className="font-semibold">{myServices.length}</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Reviews</span>
                    <span className="font-semibold">0</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Badges */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">Badges</h3>
              </div>
              <div className="card-body">
                <div className="grid grid-cols-2 gap-3">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <Award className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <div className="text-xs font-medium text-gray-500">New Member</div>
                  </div>
                  
                  {user.is_verified && (
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <Shield className="w-8 h-8 text-green-600 mx-auto mb-2" />
                      <div className="text-xs font-medium text-green-700">Verified</div>
                    </div>
                  )}
                </div>
              </div>
            </div>


            {/* My Properties */}
            {(user?.role === 'property_owner' || user?.role === 'real_estate_agent' || user?.role === 'real_estate_company' || user?.role === 'admin') && (
              <div className="card">
                <div className="card-header flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-gray-900">My Properties</h3>
                  <button
                    onClick={() => navigate('/properties/new')}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all text-sm font-medium"
                  >
                    <Plus className="w-4 h-4" />
                    List Property
                  </button>
                </div>
                <div className="card-body">
                  {loadingProperties ? (
                    <div className="text-center py-8 text-gray-500">Loading properties...</div>
                  ) : myProperties.length === 0 ? (
                    <div className="text-center py-8">
                      <Home className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-600 mb-4">You haven't listed any properties yet</p>
                      <button
                        onClick={() => navigate('/properties/new')}
                        className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all font-semibold"
                      >
                        <Plus className="w-5 h-5" />
                        List Your First Property
                      </button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {myProperties.map((property) => (
                        <div
                          key={property.id}
                          onClick={() => navigate(`/properties/${property.id}`)}
                          className="border border-gray-200 rounded-xl overflow-hidden hover:shadow-lg transition-all cursor-pointer group"
                        >
                          <div className="relative h-48">
                            <img
                              src={getImageUrl(property.images?.[0])}
                              alt={property.title}
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                            />
                            <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-semibold">
                              {property.listing_type === 'rent' ? 'For Rent' : 'For Sale'}
                            </div>
                            {property.verified && (
                              <div className="absolute top-3 left-3 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-semibold flex items-center gap-1">
                                <Shield className="w-3 h-3" />
                                Verified
                              </div>
                            )}
                          </div>
                          <div className="p-4">
                            <h4 className="font-bold text-gray-900 mb-2 line-clamp-1">{property.title}</h4>
                            <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                              <MapPin className="w-4 h-4" />
                              <span className="line-clamp-1">{property.location}</span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-lg font-bold text-blue-600">
                                {new Intl.NumberFormat('fr-CM', {
                                  style: 'currency',
                                  currency: 'XAF',
                                  minimumFractionDigits: 0
                                }).format(property.price)}
                              </span>
                              <div className="flex items-center gap-3 text-sm text-gray-500">
                                <div className="flex items-center gap-1">
                                  <Eye className="w-4 h-4" />
                                  <span>{property.views || 0}</span>
                                </div>
                                <div className="flex items-center gap-1">
                                  <Heart className="w-4 h-4" />
                                  <span>{property.favorites || 0}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Account Actions */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-gray-900">Account</h3>
              </div>
              <div className="card-body">
                <div className="space-y-3">
                  <button className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="font-medium text-gray-900">Privacy Settings</div>
                    <div className="text-sm text-gray-500">Manage your privacy preferences</div>
                  </button>
                  
                  <button className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="font-medium text-gray-900">Notification Settings</div>
                    <div className="text-sm text-gray-500">Control your notifications</div>
                  </button>
                  
                  <button className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="font-medium text-gray-900">Security</div>
                    <div className="text-sm text-gray-500">Password and security settings</div>
                  </button>
                  
                  <hr className="my-3" />
                  
                  <button
                    onClick={logout}
                    className="w-full text-left p-3 rounded-lg hover:bg-red-50 transition-colors text-red-600"
                    data-testid="logout-btn"
                  >
                    <div className="font-medium">Sign Out</div>
                    <div className="text-sm">Sign out of your account</div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;