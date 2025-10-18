import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Package, ArrowLeft } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const InventoryForm = ({ mode = 'create' }) => {
  const navigate = useNavigate();
  const { itemId } = useParams();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [properties, setProperties] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    category: 'Spare Parts',
    property_id: '',
    quantity: 0,
    unit: 'pcs',
    reorder_level: 10,
    reorder_quantity: 20,
    unit_cost: '',
    supplier_name: '',
    supplier_contact: '',
    location: '',
    notes: ''
  });

  useEffect(() => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    fetchProperties();
    if (mode === 'edit' && itemId) {
      fetchItem();
    }
  }, [user, mode, itemId]);

  const fetchProperties = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/properties`, { withCredentials: true });
      setProperties(response.data);
    } catch (error) {
      console.error('Error fetching properties:', error);
    }
  };

  const fetchItem = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/assets/inventory/${itemId}`, { withCredentials: true });
      const item = response.data;
      setFormData({
        name: item.name || '',
        category: item.category || 'Spare Parts',
        property_id: item.property_id || '',
        quantity: item.quantity || 0,
        unit: item.unit || 'pcs',
        reorder_level: item.reorder_level || 10,
        reorder_quantity: item.reorder_quantity || 20,
        unit_cost: item.unit_cost || '',
        supplier_name: item.supplier_name || '',
        supplier_contact: item.supplier_contact || '',
        location: item.location || '',
        notes: item.notes || ''
      });
    } catch (error) {
      console.error('Error fetching item:', error);
      alert('Failed to load inventory item');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...formData,
        quantity: parseInt(formData.quantity),
        reorder_level: parseInt(formData.reorder_level),
        reorder_quantity: parseInt(formData.reorder_quantity),
        unit_cost: formData.unit_cost ? parseFloat(formData.unit_cost) : null
      };

      if (mode === 'edit' && itemId) {
        await axios.put(
          `${BACKEND_URL}/api/assets/inventory/${itemId}`,
          payload,
          { withCredentials: true }
        );
        alert('Inventory item updated successfully!');
      } else {
        await axios.post(
          `${BACKEND_URL}/api/assets/inventory`,
          payload,
          { withCredentials: true }
        );
        alert('Inventory item created successfully!');
      }
      navigate('/assets/inventory');
    } catch (error) {
      console.error('Error saving item:', error);
      alert(error.response?.data?.detail || 'Failed to save inventory item');
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
            onClick={() => navigate('/assets/inventory')}
            className="text-green-600 hover:text-green-700 font-semibold mb-4 flex items-center"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Inventory
          </button>
          <h1 className="text-3xl font-bold mb-2">
            {mode === 'edit' ? 'Edit Inventory Item' : 'Add New Inventory Item'}
          </h1>
          <p className="text-gray-600">Fill in the item information</p>
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
                  Item Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="e.g., HVAC Filter - 20x25x1"
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
                  <option value="Spare Parts">Spare Parts</option>
                  <option value="Tools">Tools</option>
                  <option value="Consumables">Consumables</option>
                  <option value="Equipment">Equipment</option>
                  <option value="Safety Gear">Safety Gear</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Property (Optional)
                </label>
                <select
                  name="property_id"
                  value={formData.property_id}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="">All Properties</option>
                  {properties.map(property => (
                    <option key={property.id} value={property.id}>
                      {property.title}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Storage Location
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="e.g., Main Warehouse - Shelf A3"
                />
              </div>
            </div>
          </div>

          {/* Stock Information */}
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-4">Stock Information</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Quantity <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  name="quantity"
                  value={formData.quantity}
                  onChange={handleChange}
                  required
                  min="0"
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Unit <span className="text-red-500">*</span>
                </label>
                <select
                  name="unit"
                  value={formData.unit}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="pcs">Pieces</option>
                  <option value="kg">Kilograms</option>
                  <option value="liters">Liters</option>
                  <option value="meters">Meters</option>
                  <option value="boxes">Boxes</option>
                  <option value="rolls">Rolls</option>
                  <option value="bags">Bags</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reorder Level <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  name="reorder_level"
                  value={formData.reorder_level}
                  onChange={handleChange}
                  required
                  min="0"
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Minimum quantity before alert"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reorder Quantity <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  name="reorder_quantity"
                  value={formData.reorder_quantity}
                  onChange={handleChange}
                  required
                  min="1"
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Quantity to reorder"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Unit Cost (XAF)
                </label>
                <input
                  type="number"
                  name="unit_cost"
                  value={formData.unit_cost}
                  onChange={handleChange}
                  step="0.01"
                  min="0"
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Cost per unit"
                />
              </div>
            </div>
          </div>

          {/* Supplier Information */}
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-4">Supplier Information</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Supplier Name
                </label>
                <input
                  type="text"
                  name="supplier_name"
                  value={formData.supplier_name}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="e.g., ABC Supplies Ltd"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Supplier Contact
                </label>
                <input
                  type="text"
                  name="supplier_contact"
                  value={formData.supplier_contact}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Phone or email"
                />
              </div>
            </div>
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
              placeholder="Additional information..."
            />
          </div>

          {/* Submit Buttons */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400"
            >
              {loading ? 'Saving...' : mode === 'edit' ? 'Update Item' : 'Create Item'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/assets/inventory')}
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

export default InventoryForm;
