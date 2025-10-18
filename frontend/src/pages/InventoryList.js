import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Package, Filter, Search, Plus, AlertTriangle, Eye, Edit, TrendingDown } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const InventoryList = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: '',
    low_stock: false
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    fetchItems();
  }, [user, filters]);

  const fetchItems = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });
      
      const response = await axios.get(
        `${BACKEND_URL}/api/assets/inventory?${params.toString()}`,
        { withCredentials: true }
      );
      setItems(response.data);
    } catch (error) {
      console.error('Error fetching inventory:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    setFilters({ category: '', low_stock: false });
  };

  const filteredItems = items.filter(item =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getLowStockStatus = (item) => {
    return item.quantity <= item.reorder_level;
  };

  const getStockColor = (item) => {
    if (item.quantity === 0) return 'bg-red-100 text-red-800';
    if (getLowStockStatus(item)) return 'bg-orange-100 text-orange-800';
    return 'bg-green-100 text-green-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  const lowStockCount = items.filter(item => getLowStockStatus(item)).length;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div className="mb-4 md:mb-0">
            <h1 className="text-3xl font-bold mb-2">Inventory Management</h1>
            <p className="text-gray-600">Track parts, supplies, and equipment</p>
          </div>
          {(user?.role === 'estate_manager' || user?.role === 'admin') && (
            <button
              onClick={() => navigate('/assets/inventory/create')}
              className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 flex items-center justify-center"
            >
              <Plus className="w-5 h-5 mr-2" />
              Add Inventory Item
            </button>
          )}
        </div>

        {/* Low Stock Alert Banner */}
        {lowStockCount > 0 && (
          <div className="bg-orange-50 border-l-4 border-orange-500 p-6 mb-6 rounded-lg">
            <div className="flex items-center">
              <AlertTriangle className="w-6 h-6 text-orange-500 mr-3" />
              <div>
                <h3 className="font-bold text-orange-900 mb-1">Low Stock Alert</h3>
                <p className="text-orange-800">
                  {lowStockCount} item{lowStockCount > 1 ? 's are' : ' is'} at or below reorder level
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search inventory by name or category..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Filter Button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="bg-gray-100 hover:bg-gray-200 px-6 py-2 rounded-lg font-semibold flex items-center justify-center"
            >
              <Filter className="w-5 h-5 mr-2" />
              Filters
            </button>
          </div>

          {/* Filter Options */}
          {showFilters && (
            <div className="mt-6 pt-6 border-t grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <select
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="">All Categories</option>
                  <option value="Spare Parts">Spare Parts</option>
                  <option value="Tools">Tools</option>
                  <option value="Consumables">Consumables</option>
                  <option value="Equipment">Equipment</option>
                  <option value="Safety Gear">Safety Gear</option>
                </select>
              </div>

              <div className="flex items-end">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.low_stock}
                    onChange={(e) => handleFilterChange('low_stock', e.target.checked)}
                    className="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">Show Low Stock Only</span>
                </label>
              </div>

              <div className="flex items-end">
                <button
                  onClick={clearFilters}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Inventory Grid */}
        {filteredItems.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No inventory items found</h3>
            <p className="text-gray-500 mb-6">Start by adding your first inventory item</p>
            {(user?.role === 'estate_manager' || user?.role === 'admin') && (
              <button
                onClick={() => navigate('/assets/inventory/create')}
                className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700"
              >
                Add Item
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredItems.map((item) => (
              <div key={item.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold mb-1">{item.name}</h3>
                      <p className="text-sm text-gray-600">{item.category}</p>
                    </div>
                    {getLowStockStatus(item) && (
                      <TrendingDown className="w-6 h-6 text-orange-500" />
                    )}
                  </div>

                  <div className="space-y-3 mb-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Current Stock:</span>
                      <span className={`text-lg font-bold px-3 py-1 rounded ${getStockColor(item)}`}>
                        {item.quantity} {item.unit}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Reorder Level:</span>
                      <span className="font-medium">{item.reorder_level} {item.unit}</span>
                    </div>

                    {item.unit_cost && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Unit Cost:</span>
                        <span className="font-medium">{item.unit_cost.toLocaleString()} XAF</span>
                      </div>
                    )}

                    {item.location && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Location:</span>
                        <span className="font-medium">{item.location}</span>
                      </div>
                    )}
                  </div>

                  {getLowStockStatus(item) && (
                    <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 mb-4 text-sm">
                      <p className="text-orange-800 font-medium">
                        ⚠️ Reorder: {item.reorder_quantity} {item.unit}
                      </p>
                    </div>
                  )}

                  <div className="flex gap-2">
                    <button
                      onClick={() => navigate(`/assets/inventory/${item.id}`)}
                      className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center justify-center"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      View
                    </button>
                    {(user?.role === 'estate_manager' || user?.role === 'admin') && (
                      <button
                        onClick={() => navigate(`/assets/inventory/${item.id}/edit`)}
                        className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center"
                      >
                        <Edit className="w-4 h-4 mr-2" />
                        Edit
                      </button>
                    )}
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

export default InventoryList;
