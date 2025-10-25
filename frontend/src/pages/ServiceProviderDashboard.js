import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Wrench, Plus, Edit, Trash2, Eye, Package, TrendingUp } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const ServiceProviderDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingService, setEditingService] = useState(null);

  const serviceProviderRoles = [
    'construction_company', 'bricklayer', 'plumber', 'electrician',
    'interior_designer', 'borehole_driller', 'cleaning_company',
    'painter', 'architect', 'carpenter', 'evaluator',
    'building_material_supplier', 'furnishing_shop', 'admin'
  ];

  const serviceCategories = [
    'construction', 'bricklaying', 'plumbing', 'electrical',
    'interior_design', 'borehole_drilling', 'cleaning',
    'painting', 'architecture', 'carpentry', 'evaluation',
    'materials', 'furnishing'
  ];

  const [serviceForm, setServiceForm] = useState({
    category: 'plumbing',
    title: '',
    description: '',
    price_range: '',
    location: '',
    images: []
  });
  
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadingImages, setUploadingImages] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    
    // Check if user has service provider role
    if (!serviceProviderRoles.includes(user.role)) {
      alert('Access denied. Service provider account required.');
      navigate('/services');
      return;
    }
    
    fetchMyServices();
  }, [user]);

  const fetchMyServices = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${BACKEND_URL}/api/services`,
        { withCredentials: true }
      );
      
      // Filter to show only user's services
      const myServices = response.data.filter(s => s.provider_id === user.id);
      setServices(myServices);
    } catch (error) {
      console.error('Error fetching services:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    if (files.length + selectedFiles.length > 10) {
      alert('Maximum 10 images allowed');
      return;
    }
    
    const newFiles = files.map(file => ({
      file,
      preview: URL.createObjectURL(file)
    }));
    
    setSelectedFiles(prev => [...prev, ...newFiles]);
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => {
      const newFiles = [...prev];
      URL.revokeObjectURL(newFiles[index].preview);
      newFiles.splice(index, 1);
      return newFiles;
    });
  };

  const uploadImages = async () => {
    if (selectedFiles.length === 0) return [];
    
    try {
      setUploadingImages(true);
      const formData = new FormData();
      
      selectedFiles.forEach(({ file }) => {
        formData.append('files', file);
      });
      formData.append('entity_type', 'service');
      
      const response = await axios.post(`${BACKEND_URL}/api/upload/images`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        withCredentials: true
      });
      
      return response.data.images.map(img => img.url);
    } catch (err) {
      console.error('Error uploading images:', err);
      throw new Error('Failed to upload images');
    } finally {
      setUploadingImages(false);
    }
  };

  const handleCreateService = async (e) => {
    e.preventDefault();
    try {
      // Upload images first if any
      let imageUrls = [];
      if (selectedFiles.length > 0) {
        imageUrls = await uploadImages();
      }
      
      const serviceData = {
        ...serviceForm,
        images: imageUrls
      };
      
      const response = await axios.post(
        `${BACKEND_URL}/api/services`,
        serviceData,
        { withCredentials: true }
      );
      
      alert('Service created successfully! It will be visible after admin approval.');
      setShowCreateModal(false);
      resetForm();
      fetchMyServices();
    } catch (error) {
      console.error('Error creating service:', error);
      alert(error.response?.data?.detail || 'Failed to create service');
    }
  };

  const handleUpdateService = async (e) => {
    e.preventDefault();
    try {
      await axios.put(
        `${BACKEND_URL}/api/services/${editingService.id}`,
        serviceForm,
        { withCredentials: true }
      );
      
      alert('Service updated successfully!');
      setEditingService(null);
      resetForm();
      fetchMyServices();
    } catch (error) {
      console.error('Error updating service:', error);
      alert(error.response?.data?.detail || 'Failed to update service');
    }
  };

  const handleDeleteService = async (serviceId) => {
    if (!window.confirm('Are you sure you want to delete this service?')) return;
    
    try {
      await axios.delete(
        `${BACKEND_URL}/api/services/${serviceId}`,
        { withCredentials: true }
      );
      
      alert('Service deleted successfully!');
      fetchMyServices();
    } catch (error) {
      console.error('Error deleting service:', error);
      alert('Failed to delete service');
    }
  };

  const openEditModal = (service) => {
    setEditingService(service);
    setServiceForm({
      category: service.category,
      title: service.title,
      description: service.description,
      price_range: service.price_range || '',
      location: service.location,
      images: service.images || []
    });
    setShowCreateModal(true);
  };

  const resetForm = () => {
    setServiceForm({
      category: 'plumbing',
      title: '',
      description: '',
      price_range: '',
      location: '',
      images: []
    });
    setEditingService(null);
  };

  const handleCloseModal = () => {
    setShowCreateModal(false);
    setEditingService(null);
    resetForm();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Service Provider Dashboard</h1>
          <p className="text-gray-600">Manage your professional services</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 mb-1">Total Services</p>
                <p className="text-3xl font-bold text-green-600">{services.length}</p>
              </div>
              <Package className="w-12 h-12 text-green-600 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 mb-1">Active Services</p>
                <p className="text-3xl font-bold text-blue-600">
                  {services.filter(s => s.verification_status === 'verified').length}
                </p>
              </div>
              <TrendingUp className="w-12 h-12 text-blue-600 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 mb-1">Pending Approval</p>
                <p className="text-3xl font-bold text-orange-600">
                  {services.filter(s => s.verification_status === 'pending').length}
                </p>
              </div>
              <Wrench className="w-12 h-12 text-orange-600 opacity-20" />
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold">My Services</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 flex items-center"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add New Service
          </button>
        </div>

        {/* Services List */}
        {services.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <Wrench className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No services yet</h3>
            <p className="text-gray-500 mb-6">Start by creating your first service</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700"
            >
              Create Service
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {services.map((service) => (
              <div key={service.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold mb-1">{service.title}</h3>
                      <p className="text-sm text-gray-600">{service.category}</p>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      service.verification_status === 'verified' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-orange-100 text-orange-800'
                    }`}>
                      {service.verification_status === 'verified' ? 'Active' : 'Pending'}
                    </span>
                  </div>

                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">{service.description}</p>

                  <div className="space-y-2 mb-4 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Location:</span>
                      <span className="font-medium">{service.location}</span>
                    </div>
                    {service.price_range && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Price:</span>
                        <span className="font-medium">{service.price_range}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => navigate(`/services/${service.id}`)}
                      className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      View
                    </button>
                    <button
                      onClick={() => openEditModal(service)}
                      className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center justify-center"
                    >
                      <Edit className="w-4 h-4 mr-2" />
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteService(service.id)}
                      className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Create/Edit Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <h3 className="text-2xl font-bold mb-6">
                {editingService ? 'Edit Service' : 'Create New Service'}
              </h3>

              <form onSubmit={editingService ? handleUpdateService : handleCreateService}>
                <div className="space-y-4">
                  {/* Category */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Category <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={serviceForm.category}
                      onChange={(e) => setServiceForm({ ...serviceForm, category: e.target.value })}
                      required
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    >
                      {serviceCategories.map(cat => (
                        <option key={cat} value={cat}>{cat.replace('_', ' ').toUpperCase()}</option>
                      ))}
                    </select>
                  </div>

                  {/* Title */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Service Title <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={serviceForm.title}
                      onChange={(e) => setServiceForm({ ...serviceForm, title: e.target.value })}
                      required
                      placeholder="e.g., Professional Plumbing Services"
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>

                  {/* Description */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      value={serviceForm.description}
                      onChange={(e) => setServiceForm({ ...serviceForm, description: e.target.value })}
                      required
                      rows="4"
                      placeholder="Describe your service in detail..."
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>

                  {/* Price Range */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Price Range
                    </label>
                    <input
                      type="text"
                      value={serviceForm.price_range}
                      onChange={(e) => setServiceForm({ ...serviceForm, price_range: e.target.value })}
                      placeholder="e.g., 5000-15000 XAF/hour"
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>

                  {/* Location */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Location <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={serviceForm.location}
                      onChange={(e) => setServiceForm({ ...serviceForm, location: e.target.value })}
                      required
                      placeholder="e.g., Douala, Cameroon"
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Buttons */}
                <div className="flex gap-4 mt-6">
                  <button
                    type="submit"
                    className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700"
                  >
                    {editingService ? 'Update Service' : 'Create Service'}
                  </button>
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    className="px-6 py-3 border border-gray-300 rounded-lg font-semibold hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ServiceProviderDashboard;
