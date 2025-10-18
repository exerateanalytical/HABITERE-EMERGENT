import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { DollarSign, Filter, Search, TrendingUp } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const ExpensesList = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    expense_type: ''
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [totalExpenses, setTotalExpenses] = useState(0);

  useEffect(() => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    fetchExpenses();
  }, [user, filters]);

  const fetchExpenses = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.keys(filters).forEach(key => {
        if (filters[key]) params.append(key, filters[key]);
      });
      
      const response = await axios.get(
        `${BACKEND_URL}/api/assets/expenses?${params.toString()}`,
        { withCredentials: true }
      );
      setExpenses(response.data);
      
      // Calculate total
      const total = response.data.reduce((sum, expense) => sum + expense.amount, 0);
      setTotalExpenses(total);
    } catch (error) {
      console.error('Error fetching expenses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    setFilters({ expense_type: '' });
  };

  const filteredExpenses = expenses.filter(expense =>
    expense.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    expense.asset_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getApprovalColor = (status) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'Maintenance':
        return 'bg-blue-100 text-blue-800';
      case 'Upgrade':
        return 'bg-purple-100 text-purple-800';
      case 'Purchase':
        return 'bg-green-100 text-green-800';
      case 'Repair':
        return 'bg-orange-100 text-orange-800';
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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Expenses</h1>
          <p className="text-gray-600">Track all asset-related expenses</p>
        </div>

        {/* Total Expenses Card */}
        <div className="bg-gradient-to-r from-purple-600 to-purple-700 rounded-lg shadow-lg p-8 mb-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg mb-2 opacity-90">Total Expenses</h2>
              <p className="text-4xl font-bold">{totalExpenses.toLocaleString()} XAF</p>
            </div>
            <TrendingUp className="w-16 h-16 opacity-50" />
          </div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search expenses by description or asset..."
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
            <div className="mt-6 pt-6 border-t grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Expense Type</label>
                <select
                  value={filters.expense_type}
                  onChange={(e) => handleFilterChange('expense_type', e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="">All Types</option>
                  <option value="Maintenance">Maintenance</option>
                  <option value="Upgrade">Upgrade</option>
                  <option value="Purchase">Purchase</option>
                  <option value="Repair">Repair</option>
                </select>
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

        {/* Expenses List */}
        {filteredExpenses.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <DollarSign className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No expenses found</h3>
            <p className="text-gray-500">No expenses have been logged yet</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredExpenses.map((expense) => (
              <div key={expense.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <DollarSign className="w-6 h-6 text-purple-600" />
                      <h3 className="text-lg font-bold">{expense.description}</h3>
                    </div>
                    {expense.asset_name && (
                      <p className="text-sm text-gray-600">Asset: {expense.asset_name}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-purple-600">
                      {expense.amount.toLocaleString()} XAF
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2 mb-4">
                  <span className={`text-xs px-2 py-1 rounded-full ${getTypeColor(expense.expense_type)}`}>
                    {expense.expense_type}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded-full ${getApprovalColor(expense.approval_status)}`}>
                    {expense.approval_status === 'approved' ? 'Approved' : 
                     expense.approval_status === 'pending' ? 'Pending Approval' : 'Rejected'}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>Date: {new Date(expense.date).toLocaleDateString()}</span>
                  <span>Logged: {new Date(expense.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ExpensesList;
