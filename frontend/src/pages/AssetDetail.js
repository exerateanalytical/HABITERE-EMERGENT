import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Package, ArrowLeft, Edit, Trash2, Calendar, DollarSign, MapPin, User, FileText } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const AssetDetail = () => {
  const navigate = useNavigate();
  const { assetId } = useParams();
  const { user } = useAuth();
  const [asset, setAsset] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    fetchAsset();
  }, [user, assetId]);

  const fetchAsset = async () => {
    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/assets/${assetId}`,
        { withCredentials: true }
      );
      setAsset(response.data);
    } catch (error) {
      console.error('Error fetching asset:', error);
      alert('Failed to load asset');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this asset? This action cannot be undone.')) return;
    
    try {
      await axios.delete(`${BACKEND_URL}/api/assets/${assetId}`, { withCredentials: true });
      alert('Asset deleted successfully!');
      navigate('/assets');
    } catch (error) {
      console.error('Error deleting asset:', error);
      alert('Failed to delete asset');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
        return 'bg-green-100 text-green-800';
      case 'Under Maintenance':
        return 'bg-yellow-100 text-yellow-800';
      case 'Decommissioned':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getConditionColor = (condition) => {
    switch (condition) {
      case 'Excellent':
        return 'bg-blue-100 text-blue-800';
      case 'Good':
        return 'bg-green-100 text-green-800';
      case 'Fair':
        return 'bg-yellow-100 text-yellow-800';
      case 'Poor':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (!asset) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-700 mb-2">Asset not found</h2>
          <button
            onClick={() => navigate('/assets')}
            className="text-green-600 hover:text-green-700 font-semibold"
          >
            Back to Assets
          </button>
        </div>
      </div>
    );
  }

  const canEdit = asset.owner_id === user?.id || ['estate_manager', 'admin'].includes(user?.role);
  const canDelete = asset.owner_id === user?.id || user?.role === 'admin';

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/assets')}
            className="text-green-600 hover:text-green-700 font-semibold mb-4 flex items-center"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Assets
          </button>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-2">{asset.name}</h1>
              <p className="text-gray-600">{asset.category}</p>
            </div>
            <div className="flex gap-3">
              {canEdit && (
                <button
                  onClick={() => navigate(`/assets/${assetId}/edit`)}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 flex items-center"
                >
                  <Edit className="w-5 h-5 mr-2" />
                  Edit
                </button>
              )}
              {canDelete && (
                <button
                  onClick={handleDelete}
                  className="bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 flex items-center"
                >
                  <Trash2 className="w-5 h-5 mr-2" />
                  Delete
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Status Badges */}
        <div className="flex gap-3 mb-8">
          <span className={`px-4 py-2 rounded-full font-semibold ${getStatusColor(asset.status)}`}>
            {asset.status}
          </span>
          <span className={`px-4 py-2 rounded-full font-semibold ${getConditionColor(asset.condition)}`}>
            {asset.condition} Condition
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Information */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Info */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <Package className="w-6 h-6 mr-2 text-green-600" />
                Basic Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">Location</label>
                  <p className="text-gray-900 flex items-center mt-1">
                    <MapPin className="w-4 h-4 mr-2 text-gray-400" />
                    {asset.location}
                  </p>
                </div>
                {asset.serial_number && (
                  <div>
                    <label className="text-sm font-medium text-gray-600">Serial Number</label>
                    <p className="text-gray-900 mt-1">{asset.serial_number}</p>
                  </div>
                )}
                {asset.acquisition_date && (
                  <div>
                    <label className="text-sm font-medium text-gray-600">Acquisition Date</label>
                    <p className="text-gray-900 mt-1">{new Date(asset.acquisition_date).toLocaleDateString()}</p>
                  </div>
                )}
                {asset.purchase_value && (
                  <div>
                    <label className="text-sm font-medium text-gray-600">Purchase Value</label>
                    <p className="text-gray-900 flex items-center mt-1">
                      <DollarSign className="w-4 h-4 mr-1 text-gray-400" />
                      {asset.purchase_value.toLocaleString()} XAF
                    </p>
                  </div>
                )}
                {asset.depreciation_rate && (
                  <div>
                    <label className="text-sm font-medium text-gray-600">Depreciation Rate</label>
                    <p className="text-gray-900 mt-1">{asset.depreciation_rate}% per year</p>
                  </div>
                )}
              </div>
            </div>

            {/* Maintenance Schedule */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <Calendar className="w-6 h-6 mr-2 text-blue-600" />
                Maintenance Schedule
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {asset.last_maintenance_date && (
                  <div>
                    <label className="text-sm font-medium text-gray-600">Last Maintenance</label>
                    <p className="text-gray-900 mt-1">{new Date(asset.last_maintenance_date).toLocaleDateString()}</p>
                  </div>
                )}
                {asset.next_maintenance_date && (
                  <div>
                    <label className="text-sm font-medium text-gray-600">Next Maintenance</label>
                    <p className="text-gray-900 mt-1">{new Date(asset.next_maintenance_date).toLocaleDateString()}</p>
                  </div>
                )}
              </div>
              <div className="mt-4">
                <button
                  onClick={() => navigate('/assets/maintenance/create', { state: { assetId: asset.id } })}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700"
                >
                  Schedule Maintenance
                </button>
              </div>
            </div>

            {/* Notes */}
            {asset.notes && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold mb-4 flex items-center">
                  <FileText className="w-6 h-6 mr-2 text-gray-600" />
                  Notes
                </h2>
                <p className="text-gray-700 whitespace-pre-wrap">{asset.notes}</p>
              </div>
            )}

            {/* Documents */}
            {asset.documents && asset.documents.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold mb-4">Documents</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {asset.documents.map((doc, index) => (
                    <div key={index} className="bg-gray-100 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 mb-2">Document {index + 1}</div>
                      <a
                        href={doc}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-green-600 hover:text-green-700 text-sm font-semibold"
                      >
                        View
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-bold mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/assets/maintenance', { state: { assetId: asset.id } })}
                  className="w-full bg-blue-100 hover:bg-blue-200 p-3 rounded-lg text-left text-blue-800 font-semibold"
                >
                  View Maintenance Tasks
                </button>
                <button
                  onClick={() => navigate('/assets/expenses', { state: { assetId: asset.id } })}
                  className="w-full bg-purple-100 hover:bg-purple-200 p-3 rounded-lg text-left text-purple-800 font-semibold"
                >
                  View Expenses
                </button>
              </div>
            </div>

            {/* Metadata */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-bold mb-4">Details</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <label className="text-gray-600">Created</label>
                  <p className="text-gray-900">{new Date(asset.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <label className="text-gray-600">Last Updated</label>
                  <p className="text-gray-900">{new Date(asset.updated_at).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssetDetail;
