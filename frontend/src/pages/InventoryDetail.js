import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Package, ArrowLeft, Edit, Trash2, Plus, Minus, AlertTriangle, DollarSign, MapPin, Phone } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const InventoryDetail = () => {
  const navigate = useNavigate();
  const { itemId } = useParams();
  const { user } = useAuth();
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAdjustModal, setShowAdjustModal] = useState(false);
  const [adjustment, setAdjustment] = useState({
    type: 'add',
    quantity: 0,
    reason: ''
  });

  useEffect(() => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    fetchItem();
  }, [user, itemId]);

  const fetchItem = async () => {
    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/assets/inventory/${itemId}`,
        { withCredentials: true }
      );
      setItem(response.data);
    } catch (error) {
      console.error('Error fetching item:', error);
      alert('Failed to load inventory item');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this inventory item?')) return;
    
    try {
      await axios.delete(`${BACKEND_URL}/api/assets/inventory/${itemId}`, { withCredentials: true });
      alert('Inventory item deleted successfully!');
      navigate('/assets/inventory');
    } catch (error) {
      console.error('Error deleting item:', error);
      alert('Failed to delete inventory item');
    }
  };

  const handleAdjustStock = async () => {
    if (!adjustment.quantity || adjustment.quantity <= 0) {
      alert('Please enter a valid quantity');
      return;
    }

    try {
      await axios.post(
        `${BACKEND_URL}/api/assets/inventory/${itemId}/adjust-stock`,
        adjustment,
        { withCredentials: true }
      );
      alert('Stock adjusted successfully!');
      setShowAdjustModal(false);
      setAdjustment({ type: 'add', quantity: 0, reason: '' });
      fetchItem();
    } catch (error) {
      console.error('Error adjusting stock:', error);
      alert(error.response?.data?.detail || 'Failed to adjust stock');
    }
  };

  const getLowStockStatus = () => {
    return item && item.quantity <= item.reorder_level;
  };

  const getStockColor = () => {
    if (!item) return 'bg-gray-100 text-gray-800';
    if (item.quantity === 0) return 'bg-red-100 text-red-800';
    if (getLowStockStatus()) return 'bg-orange-100 text-orange-800';
    return 'bg-green-100 text-green-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (!item) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-700 mb-2">Item not found</h2>
          <button
            onClick={() => navigate('/assets/inventory')}
            className="text-green-600 hover:text-green-700 font-semibold"
          >
            Back to Inventory
          </button>
        </div>
      </div>
    );
  }

  const canEdit = ['estate_manager', 'admin'].includes(user?.role);
  const canAdjust = ['estate_manager', 'technician', 'admin'].includes(user?.role);
  const canDelete = user?.role === 'admin';

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/assets/inventory')}
            className="text-green-600 hover:text-green-700 font-semibold mb-4 flex items-center"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Inventory
          </button>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-2">{item.name}</h1>
              <p className="text-gray-600">{item.category}</p>
            </div>
            <div className="flex gap-3">
              {canEdit && (
                <button
                  onClick={() => navigate(`/assets/inventory/${itemId}/edit`)}
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

        {/* Low Stock Alert */}
        {getLowStockStatus() && (
          <div className="bg-orange-50 border-l-4 border-orange-500 p-6 mb-6 rounded-lg">
            <div className="flex items-center">
              <AlertTriangle className="w-6 h-6 text-orange-500 mr-3" />
              <div>
                <h3 className="font-bold text-orange-900 mb-1">Low Stock Alert</h3>
                <p className="text-orange-800">
                  Current stock ({item.quantity} {item.unit}) is at or below reorder level. 
                  Recommended reorder quantity: {item.reorder_quantity} {item.unit}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Information */}
          <div className="lg:col-span-2 space-y-6">
            {/* Stock Status */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <Package className="w-6 h-6 mr-2 text-green-600" />
                Stock Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <label className="text-sm text-gray-600 block mb-2">Current Stock</label>
                  <div className={`text-3xl font-bold px-4 py-3 rounded-lg ${getStockColor()}`}>
                    {item.quantity} {item.unit}
                  </div>
                </div>
                <div className="text-center">
                  <label className="text-sm text-gray-600 block mb-2">Reorder Level</label>
                  <div className="text-2xl font-bold text-gray-900">
                    {item.reorder_level} {item.unit}
                  </div>
                </div>
                <div className="text-center">
                  <label className="text-sm text-gray-600 block mb-2">Reorder Quantity</label>
                  <div className="text-2xl font-bold text-gray-900">
                    {item.reorder_quantity} {item.unit}
                  </div>
                </div>
              </div>

              {canAdjust && (
                <div className="mt-6 pt-6 border-t">
                  <button
                    onClick={() => setShowAdjustModal(true)}
                    className="w-full bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700"
                  >
                    Adjust Stock
                  </button>
                </div>
              )}
            </div>

            {/* Details */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4">Item Details</h2>
              <div className="space-y-4">
                {item.location && (
                  <div className="flex items-start">
                    <MapPin className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                    <div>
                      <label className="text-sm text-gray-600">Storage Location</label>
                      <p className="text-gray-900 font-medium">{item.location}</p>
                    </div>
                  </div>
                )}

                {item.unit_cost && (
                  <div className="flex items-start">
                    <DollarSign className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                    <div>
                      <label className="text-sm text-gray-600">Unit Cost</label>
                      <p className="text-gray-900 font-medium">{item.unit_cost.toLocaleString()} XAF</p>
                      <p className="text-sm text-gray-500 mt-1">
                        Total value: {(item.quantity * item.unit_cost).toLocaleString()} XAF
                      </p>
                    </div>
                  </div>
                )}

                {item.notes && (
                  <div>
                    <label className="text-sm text-gray-600 block mb-2">Notes</label>
                    <p className="text-gray-900 whitespace-pre-wrap">{item.notes}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Supplier Info */}
            {(item.supplier_name || item.supplier_contact) && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold mb-4">Supplier Information</h2>
                <div className="space-y-3">
                  {item.supplier_name && (
                    <div>
                      <label className="text-sm text-gray-600">Supplier Name</label>
                      <p className="text-gray-900 font-medium">{item.supplier_name}</p>
                    </div>
                  )}
                  {item.supplier_contact && (
                    <div className="flex items-center">
                      <Phone className="w-4 h-4 text-gray-400 mr-2" />
                      <span className="text-gray-900">{item.supplier_contact}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Metadata */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-bold mb-4">Details</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <label className="text-gray-600">Created</label>
                  <p className="text-gray-900">{new Date(item.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <label className="text-gray-600">Last Updated</label>
                  <p className="text-gray-900">{new Date(item.updated_at).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Adjust Stock Modal */}
        {showAdjustModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              <h3 className="text-xl font-bold mb-4">Adjust Stock</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Adjustment Type
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => setAdjustment({ ...adjustment, type: 'add' })}
                      className={`px-4 py-3 rounded-lg font-semibold flex items-center justify-center ${
                        adjustment.type === 'add'
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      <Plus className="w-5 h-5 mr-2" />
                      Add Stock
                    </button>
                    <button
                      onClick={() => setAdjustment({ ...adjustment, type: 'subtract' })}
                      className={`px-4 py-3 rounded-lg font-semibold flex items-center justify-center ${
                        adjustment.type === 'subtract'
                          ? 'bg-red-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      <Minus className="w-5 h-5 mr-2" />
                      Remove Stock
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quantity
                  </label>
                  <input
                    type="number"
                    value={adjustment.quantity}
                    onChange={(e) => setAdjustment({ ...adjustment, quantity: parseInt(e.target.value) })}
                    min="1"
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Reason
                  </label>
                  <textarea
                    value={adjustment.reason}
                    onChange={(e) => setAdjustment({ ...adjustment, reason: e.target.value })}
                    rows="3"
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="e.g., Used for maintenance, New delivery, etc."
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleAdjustStock}
                  className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700"
                >
                  Confirm
                </button>
                <button
                  onClick={() => {
                    setShowAdjustModal(false);
                    setAdjustment({ type: 'add', quantity: 0, reason: '' });
                  }}
                  className="px-6 py-3 border border-gray-300 rounded-lg font-semibold hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InventoryDetail;
