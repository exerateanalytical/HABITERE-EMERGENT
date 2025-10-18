import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Package, Upload, X, ArrowLeft } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const AssetForm = ({ mode = 'create' }) => {
  const navigate = useNavigate();
  const { assetId } = useParams();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [properties, setProperties] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    category: 'Building Equipment',
    property_id: '',
    location: '',
    status: 'Active',
    condition: 'Good',
    serial_number: '',
    acquisition_date: '',
    purchase_value: '',
    assigned_to: '',
    last_maintenance_date: '',
    next_maintenance_date: '',
    depreciation_rate: '',
    notes: ''
  });
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    fetchProperties();
    if (mode === 'edit' && assetId) {
      fetchAsset();
    }
  }, [user, mode, assetId]);

  const fetchProperties = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/properties`, { withCredentials: true });
      setProperties(response.data);
    } catch (error) {
      console.error('Error fetching properties:', error);
    }
  };

  const fetchAsset = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/assets/${assetId}`, { withCredentials: true });
      const asset = response.data;
      setFormData({
        name: asset.name || '',
        category: asset.category || 'Building Equipment',
        property_id: asset.property_id || '',
        location: asset.location || '',
        status: asset.status || 'Active',
        condition: asset.condition || 'Good',
        serial_number: asset.serial_number || '',
        acquisition_date: asset.acquisition_date || '',
        purchase_value: asset.purchase_value || '',
        assigned_to: asset.assigned_to || '',
        last_maintenance_date: asset.last_maintenance_date || '',
        next_maintenance_date: asset.next_maintenance_date || '',
        depreciation_rate: asset.depreciation_rate || '',
        notes: asset.notes || ''
      });
      if (asset.documents) {
        setDocuments(asset.documents);
      }
    } catch (error) {
      console.error('Error fetching asset:', error);
      alert('Failed to load asset');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setUploading(true);
    try {
      const uploadPromises = files.map(async (file) => {
        const formData = new FormData();
        formData.append('files', file);
        formData.append('entity_type', 'asset');
        formData.append('entity_id', assetId || 'new');

        const response = await axios.post(
          `${BACKEND_URL}/api/upload/images`,
          formData,
          { withCredentials: true }
        );
        return response.data.urls[0];
      });

      const uploadedUrls = await Promise.all(uploadPromises);
      setDocuments(prev => [...prev, ...uploadedUrls]);
    } catch (error) {
      console.error('Error uploading files:', error);
      alert('Failed to upload files');
    } finally {
      setUploading(false);
    }
  };

  const removeDocument = (index) => {
    setDocuments(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...formData,
        documents,
        purchase_value: formData.purchase_value ? parseFloat(formData.purchase_value) : null,
        depreciation_rate: formData.depreciation_rate ? parseFloat(formData.depreciation_rate) : null
      };

      if (mode === 'edit' && assetId) {
        await axios.put(
          `${BACKEND_URL}/api/assets/${assetId}`,
          payload,
          { withCredentials: true }
        );
        alert('Asset updated successfully!');
      } else {
        await axios.post(
          `${BACKEND_URL}/api/assets`,
          payload,
          { withCredentials: true }
        );
        alert('Asset created successfully!');
      }
      navigate('/assets');
    } catch (error) {
      console.error('Error saving asset:', error);
      alert(error.response?.data?.detail || 'Failed to save asset');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/assets')}
            className="text-green-600 hover:text-green-700 font-semibold mb-4 flex items-center"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Assets
          </button>
          <h1 className="text-3xl font-bold mb-2">
            {mode === 'edit' ? 'Edit Asset' : 'Add New Asset'}
          </h1>
          <p className="text-gray-600">Fill in the asset information</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6">
          {/* Basic Information */}
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-4 flex items-center">
              <Package className="w-6 h-6 mr-2 text-green-600" />
              Basic Information
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Asset Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="e.g., HVAC System - Building A"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category <span className="text-red-500">*</span>
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="Real Estate">Real Estate</option>
                  <option value="Building Equipment">Building Equipment</option>
                  <option value="Infrastructure">Infrastructure</option>
                  <option value="Furniture">Furniture</option>
                  <option value="Vehicle">Vehicle</option>
                  <option value="Tool">Tool</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Property <span className="text-red-500">*</span>
                </label>
                <select
                  name="property_id"
                  value={formData.property_id}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="">Select Property</option>
                  {properties.map(property => (
                    <option key={property.id} value={property.id}>
                      {property.title}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="e.g., Building A - 2nd Floor"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="Active">Active</option>
                  <option value="Under Maintenance">Under Maintenance</option>
                  <option value="Decommissioned">Decommissioned</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Condition
                </label>
                <select
                  name="condition"
                  value={formData.condition}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="Excellent">Excellent</option>
                  <option value="Good">Good</option>
                  <option value="Fair">Fair</option>
                  <option value="Poor">Poor</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Serial Number
                </label>
                <input
                  type="text"
                  name="serial_number"
                  value={formData.serial_number}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="e.g., SN12345678"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Acquisition Date
                </label>
                <input
                  type="date"
                  name="acquisition_date"
                  value={formData.acquisition_date}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Purchase Value (XAF)
                </label>
                <input
                  type="number"
                  name="purchase_value"
                  value={formData.purchase_value}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="e.g., 5000000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Depreciation Rate (%/year)
                </label>
                <input
                  type="number"
                  name="depreciation_rate"
                  value={formData.depreciation_rate}
                  onChange={handleChange}
                  step="0.1"
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="e.g., 10"
                />
              </div>
            </div>
          </div>

          {/* Maintenance Dates */}
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-4">Maintenance Schedule</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Last Maintenance Date
                </label>
                <input
                  type="date"
                  name="last_maintenance_date"
                  value={formData.last_maintenance_date}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Next Maintenance Date
                </label>
                <input
                  type="date"
                  name="next_maintenance_date"
                  value={formData.next_maintenance_date}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Documents */}
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-4">Documents</h2>
            
            <div className="mb-4">
              <label className="flex items-center justify-center w-full px-4 py-8 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-green-500 transition-colors">
                <div className="text-center">
                  <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <span className="text-sm text-gray-600">
                    {uploading ? 'Uploading...' : 'Click to upload documents'}
                  </span>
                  <span className="text-xs text-gray-500 block mt-1">
                    PDF, DOC, XLS, Images
                  </span>
                </div>
                <input
                  type="file"
                  multiple
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={uploading}
                />
              </label>
            </div>

            {documents.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {documents.map((doc, index) => (
                  <div key={index} className="relative">
                    <div className="bg-gray-100 p-4 rounded-lg">
                      <div className="text-sm text-gray-600 truncate">
                        Document {index + 1}
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeDocument(index)}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Notes */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows="4"
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Additional information about the asset..."
            />
          </div>

          {/* Submit Buttons */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400"
            >
              {loading ? 'Saving...' : mode === 'edit' ? 'Update Asset' : 'Create Asset'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/assets')}
              className="px-6 py-3 border border-gray-300 rounded-lg font-semibold hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AssetForm;
