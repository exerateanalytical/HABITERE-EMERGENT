import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { 
  Building, Search, CheckCircle, XCircle, Clock, Filter, 
  ChevronLeft, ChevronRight, AlertCircle, Eye, MapPin, DollarSign
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const AdminProperties = () => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(20);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('pending');
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  useEffect(() => {
    fetchProperties();
  }, [page, statusFilter]);

  const fetchProperties = async () => {
    try {
      setLoading(true);
      const params = {
        skip: page * limit,
        limit,
        ...(statusFilter && { verification_status: statusFilter }),
        ...(search && { search })
      };
      
      const response = await axios.get(`${BACKEND_URL}/api/admin/properties`, {
        params,
        withCredentials: true
      });
      
      setProperties(response.data.properties);
      setTotal(response.data.total);
      setError(null);
    } catch (err) {
      console.error('Error fetching properties:', err);
      setError(err.response?.data?.detail || 'Failed to load properties');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (propertyId) => {
    if (!window.confirm('Are you sure you want to verify this property?')) return;
    
    try {
      setActionLoading(true);
      await axios.put(`${BACKEND_URL}/api/admin/properties/${propertyId}/verify`, {}, {
        withCredentials: true
      });
      alert('Property verified successfully!');
      fetchProperties();
    } catch (err) {
      console.error('Error verifying property:', err);
      alert(err.response?.data?.detail || 'Failed to verify property');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async (propertyId) => {
    if (!rejectReason.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }
    
    try {
      setActionLoading(true);
      await axios.put(`${BACKEND_URL}/api/admin/properties/${propertyId}/reject?reason=${encodeURIComponent(rejectReason)}`, {}, {
        withCredentials: true
      });
      alert('Property rejected');
      setShowRejectModal(false);
      setRejectReason('');
      setSelectedProperty(null);
      fetchProperties();
    } catch (err) {
      console.error('Error rejecting property:', err);
      alert(err.response?.data?.detail || 'Failed to reject property');
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: Clock },
      verified: { bg: 'bg-green-100', text: 'text-green-800', icon: CheckCircle },
      rejected: { bg: 'bg-red-100', text: 'text-red-800', icon: XCircle }
    };
    
    const badge = badges[status] || badges.pending;
    const Icon = badge.icon;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
        <Icon className="w-3 h-3 mr-1" />
        {status}
      </span>
    );
  };

  const totalPages = Math.ceil(total / limit);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Link to="/admin" className="btn-primary">
            Back to Admin Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div>
            <Link to="/admin" className="text-blue-600 hover:text-blue-700 text-sm mb-2 inline-block">
              ← Back to Dashboard
            </Link>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 flex items-center">
              <Building className="w-8 h-8 mr-3" />
              Property Moderation
            </h1>
            <p className="mt-1 text-sm text-gray-500">Total: {total} properties</p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Search className="w-4 h-4 inline mr-1" />
                Search
              </label>
              <input
                type="text"
                placeholder="Title, location, description..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && fetchProperties()}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Filter className="w-4 h-4 inline mr-1" />
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="verified">Verified</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
          </div>
          
          <button onClick={fetchProperties} className="mt-4 btn-primary">
            Apply Filters
          </button>
        </div>

        {/* Properties Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            <div className="col-span-full flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : properties.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <Building className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No properties found</p>
            </div>
          ) : (
            properties.map((property) => (
              <div key={property.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                <div className="h-48 bg-gray-200 relative">
                  {property.images && property.images.length > 0 ? (
                    <img
                      src={property.images[0]}
                      alt={property.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Building className="w-16 h-16 text-gray-400" />
                    </div>
                  )}
                  <div className="absolute top-2 right-2">
                    {getStatusBadge(property.verification_status)}
                  </div>
                </div>
                
                <div className="p-4">
                  <h3 className="font-bold text-lg text-gray-900 mb-2 line-clamp-1">{property.title}</h3>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-sm text-gray-600">
                      <MapPin className="w-4 h-4 mr-1" />
                      {property.location}
                    </div>
                    <div className="flex items-center text-sm text-gray-900 font-semibold">
                      <DollarSign className="w-4 h-4 mr-1" />
                      {property.price?.toLocaleString()} {property.currency}
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Eye className="w-4 h-4 mr-1" />
                      {property.views || 0} views
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-4">
                    Owner: {property.owner_name || 'Unknown'}
                  </p>
                  
                  {property.verification_status === 'pending' && (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleVerify(property.id)}
                        disabled={actionLoading}
                        className="flex-1 bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 text-sm flex items-center justify-center"
                      >
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Verify
                      </button>
                      <button
                        onClick={() => {
                          setSelectedProperty(property);
                          setShowRejectModal(true);
                        }}
                        disabled={actionLoading}
                        className="flex-1 bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50 text-sm flex items-center justify-center"
                      >
                        <XCircle className="w-4 h-4 mr-1" />
                        Reject
                      </button>
                    </div>
                  )}
                  
                  <button
                    onClick={() => {
                      setSelectedProperty(property);
                      setShowDetailsModal(true);
                    }}
                    className="w-full mt-2 border border-gray-300 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm"
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-6 flex items-center justify-between">
            <p className="text-sm text-gray-700">
              Showing {page * limit + 1} to {Math.min((page + 1) * limit, total)} of {total}
            </p>
            <div className="flex space-x-2">
              <button
                onClick={() => setPage(Math.max(0, page - 1))}
                disabled={page === 0}
                className="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="px-4 py-2 border rounded-lg bg-white">
                Page {page + 1} of {totalPages}
              </span>
              <button
                onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                disabled={page >= totalPages - 1}
                className="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Reject Property</h3>
            <p className="text-sm text-gray-600 mb-4">
              Provide a reason for rejecting "{selectedProperty?.title}":
            </p>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="e.g., Incomplete information, Invalid images, etc."
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 mb-4"
              rows="4"
            />
            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setSelectedProperty(null);
                  setRejectReason('');
                }}
                className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => handleReject(selectedProperty.id)}
                disabled={actionLoading || !rejectReason.trim()}
                className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {actionLoading ? 'Rejecting...' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Details Modal */}
      {showDetailsModal && selectedProperty && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full my-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">{selectedProperty.title}</h3>
            <div className="space-y-3 text-sm">
              <p><strong>Location:</strong> {selectedProperty.location}</p>
              <p><strong>Price:</strong> {selectedProperty.price?.toLocaleString()} {selectedProperty.currency}</p>
              <p><strong>Type:</strong> {selectedProperty.listing_type}</p>
              <p><strong>Bedrooms:</strong> {selectedProperty.bedrooms}</p>
              <p><strong>Bathrooms:</strong> {selectedProperty.bathrooms}</p>
              <p><strong>Area:</strong> {selectedProperty.area_sqm} sqm</p>
              <p><strong>Owner:</strong> {selectedProperty.owner_name} ({selectedProperty.owner_email})</p>
              <p><strong>Description:</strong> {selectedProperty.description}</p>
              <p><strong>Status:</strong> {getStatusBadge(selectedProperty.verification_status)}</p>
              {selectedProperty.rejection_reason && (
                <p className="text-red-600"><strong>Rejection Reason:</strong> {selectedProperty.rejection_reason}</p>
              )}
            </div>
            <button
              onClick={() => {
                setShowDetailsModal(false);
                setSelectedProperty(null);
              }}
              className="mt-6 w-full btn-primary"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminProperties;
