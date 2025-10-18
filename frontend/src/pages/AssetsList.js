import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Package, Search, Filter, Plus, Eye, Edit, Trash2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const AssetsList = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: '',
    status: '',
    condition: '',
    search: ''
  });

  const categories = ['Real Estate', 'Building Equipment', 'Infrastructure', 'Furniture', 'Vehicle', 'Tool'];
  const statuses = ['Active', 'Under Maintenance', 'Decommissioned'];
  const conditions = ['Excellent', 'Good', 'Fair', 'Poor'];

  useEffect(() => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    fetchAssets();
  }, [user, filters]);

  const fetchAssets = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.category) params.append('category', filters.category);
      if (filters.status) params.append('status', filters.status);
      if (filters.condition) params.append('condition', filters.condition);
      
      const response = await axios.get(`${BACKEND_URL}/api/assets/?${params}`, { withCredentials: true });
      setAssets(response.data);
    } catch (error) {
      console.error('Error fetching assets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (assetId) => {
    if (!window.confirm('Are you sure you want to delete this asset?')) return;
    
    try {
      await axios.delete(`${BACKEND_URL}/api/assets/${assetId}`, { withCredentials: true });
      alert('Asset deleted successfully');
      fetchAssets();
    } catch (error) {
      console.error('Error deleting asset:', error);
      alert(error.response?.data?.detail || 'Failed to delete asset');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'Active': 'bg-green-100 text-green-800',
      'Under Maintenance': 'bg-orange-100 text-orange-800',
      'Decommissioned': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getConditionColor = (condition) => {
    const colors = {
      'Excellent': 'text-green-600',
      'Good': 'text-blue-600',
      'Fair': 'text-orange-600',
      'Poor': 'text-red-600'
    };
    return colors[condition] || 'text-gray-600';
  };

  const filteredAssets = assets.filter(asset =>
    asset.name.toLowerCase().includes(filters.search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Assets</h1>
            <p className="text-gray-600">Manage your property assets</p>
          </div>
          <button
            onClick={() => navigate('/assets/create')}
            className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 flex items-center"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add Asset
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search assets..."
                  className="w-full pl-10 pr-4 py-2 border rounded-lg"
                  value={filters.search}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Category</label>
              <select
                className="w-full px-4 py-2 border rounded-lg"
                value={filters.category}
                onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              >
                <option value="">All Categories</option>
                {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Status</label>
              <select
                className="w-full px-4 py-2 border rounded-lg"
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              >
                <option value="">All Statuses</option>
                {statuses.map(status => <option key={status} value={status}>{status}</option>)}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Condition</label>
              <select
                className="w-full px-4 py-2 border rounded-lg"
                value={filters.condition}
                onChange={(e) => setFilters({ ...filters, condition: e.target.value })}
              >
                <option value="">All Conditions</option>
                {conditions.map(cond => <option key={cond} value={cond}>{cond}</option>)}
              </select>
            </div>
          </div>
        </div>

        {/* Assets Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading assets...</p>
          </div>
        ) : filteredAssets.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold mb-2">No assets found</h3>
            <p className="text-gray-600 mb-6">Get started by adding your first asset</p>
            <button
              onClick={() => navigate('/assets/create')}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
            >
              Add Asset
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAssets.map((asset) => (
              <div key={asset.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow">
                <div className="h-48 bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
                  <Package className="w-20 h-20 text-white" />
                </div>
                
                <div className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-xl font-bold">{asset.name}</h3>
                    <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(asset.status)}`}>
                      {asset.status}
                    </span>
                  </div>
                  
                  <div className="space-y-2 mb-4 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Category</span>
                      <span className="font-semibold">{asset.category}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Condition</span>
                      <span className={`font-semibold ${getConditionColor(asset.condition)}`}>
                        {asset.condition}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Location</span>
                      <span className="font-semibold text-sm">{asset.location}</span>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => navigate(`/assets/${asset.id}`)}
                      className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </button>
                    <button
                      onClick={() => handleDelete(asset.id)}
                      className="bg-red-600 text-white p-2 rounded-lg hover:bg-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AssetsList;