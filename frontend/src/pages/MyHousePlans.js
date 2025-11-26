import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import {
  Home, Plus, Eye, Trash2, Download, Share2, Calculator,
  Building, Layers, Clock, DollarSign, FileText, AlertCircle,
  TrendingUp, Users, Package, Zap
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const MyHousePlans = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteModal, setDeleteModal] = useState({ show: false, planId: null });

  useEffect(() => {
    if (user) {
      fetchPlans();
    }
  }, [user]);

  const fetchPlans = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${BACKEND_URL}/api/house-plans/my-plans`,
        { withCredentials: true }
      );
      setPlans(response.data.plans);
    } catch (error) {
      console.error('Error fetching plans:', error);
      setError('Failed to load house plans');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (planId) => {
    try {
      await axios.delete(
        `${BACKEND_URL}/api/house-plans/${planId}`,
        { withCredentials: true }
      );
      setPlans(plans.filter(p => p.id !== planId));
      setDeleteModal({ show: false, planId: null });
      alert('Plan deleted successfully');
    } catch (error) {
      console.error('Error deleting plan:', error);
      alert('Failed to delete plan');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CM', {
      style: 'currency',
      currency: 'XAF',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Authentication Required</h2>
          <p className="text-gray-600 mb-6">Please login to view your house plans</p>
          <button
            onClick={() => navigate('/auth/login')}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium"
          >
            Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-xl shadow-lg p-8 mb-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-black mb-2 flex items-center">
                <Home className="w-8 h-8 mr-3" />
                My House Plans
              </h1>
              <p className="text-green-50">
                Manage your building projects and cost estimates
              </p>
            </div>
            <Link
              to="/house-plans/builder"
              className="bg-white text-green-600 hover:bg-green-50 px-6 py-3 rounded-lg font-bold flex items-center shadow-lg"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create New Plan
            </Link>
          </div>
          
          {/* Stats */}
          {plans.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                <div className="text-white/80 text-sm">Total Plans</div>
                <div className="text-2xl font-bold">{plans.length}</div>
              </div>
              <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                <div className="text-white/80 text-sm">Avg. Cost</div>
                <div className="text-2xl font-bold">
                  {formatCurrency(plans.reduce((sum, p) => sum + p.total_project_cost, 0) / plans.length)}
                </div>
              </div>
              <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                <div className="text-white/80 text-sm">Total Area</div>
                <div className="text-2xl font-bold">
                  {plans.reduce((sum, p) => sum + p.total_floor_area, 0).toFixed(0)} m²
                </div>
              </div>
              <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                <div className="text-white/80 text-sm">Avg. Duration</div>
                <div className="text-2xl font-bold">
                  {Math.round(plans.reduce((sum, p) => sum + p.estimated_duration_days, 0) / plans.length)} days
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your plans...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6 mb-6">
            <div className="flex items-center">
              <AlertCircle className="w-6 h-6 text-red-600 mr-3" />
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && plans.length === 0 && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <FileText className="w-12 h-12 text-green-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">No House Plans Yet</h3>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Start planning your dream home with our advanced house plan builder. 
              Get accurate material and cost estimates instantly.
            </p>
            <Link
              to="/house-plans/builder"
              className="inline-flex items-center bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-lg font-bold"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create Your First Plan
            </Link>
          </div>
        )}

        {/* Plans Grid */}
        {!loading && plans.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className="bg-white rounded-xl shadow-lg overflow-hidden border-2 border-gray-100 hover:border-green-300 transition-all hover:shadow-xl"
              >
                {/* Plan Header */}
                <div className="bg-gradient-to-r from-green-500 to-blue-500 p-6 text-white">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
                      <p className="text-green-50 text-sm line-clamp-2">
                        {plan.description || 'No description'}
                      </p>
                    </div>
                    <div className="ml-4">
                      <span className="inline-block px-3 py-1 bg-white/20 rounded-full text-xs font-medium capitalize">
                        {plan.house_type.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                  
                  {/* Quick Stats */}
                  <div className="grid grid-cols-3 gap-3 mt-4">
                    <div className="bg-white/10 backdrop-blur rounded-lg p-3">
                      <Layers className="w-5 h-5 mb-1" />
                      <div className="text-xs text-white/80">Floors</div>
                      <div className="font-bold">{plan.floors?.length || 0}</div>
                    </div>
                    <div className="bg-white/10 backdrop-blur rounded-lg p-3">
                      <Building className="w-5 h-5 mb-1" />
                      <div className="text-xs text-white/80">Area</div>
                      <div className="font-bold">{plan.total_floor_area?.toFixed(0)} m²</div>
                    </div>
                    <div className="bg-white/10 backdrop-blur rounded-lg p-3">
                      <Clock className="w-5 h-5 mb-1" />
                      <div className="text-xs text-white/80">Duration</div>
                      <div className="font-bold">{plan.estimated_duration_days} days</div>
                    </div>
                  </div>
                </div>

                {/* Plan Details */}
                <div className="p-6">
                  {/* Cost Breakdown */}
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="border-2 border-gray-200 rounded-lg p-4">
                      <div className="flex items-center text-gray-600 text-sm mb-1">
                        <Package className="w-4 h-4 mr-1" />
                        Materials
                      </div>
                      <div className="text-lg font-bold text-gray-900">
                        {formatCurrency(plan.total_materials_cost)}
                      </div>
                    </div>
                    <div className="border-2 border-gray-200 rounded-lg p-4">
                      <div className="flex items-center text-gray-600 text-sm mb-1">
                        <Users className="w-4 h-4 mr-1" />
                        Labor
                      </div>
                      <div className="text-lg font-bold text-gray-900">
                        {formatCurrency(plan.labor_cost)}
                      </div>
                    </div>
                  </div>

                  <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4 mb-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center text-green-700 font-medium">
                        <DollarSign className="w-5 h-5 mr-2" />
                        Total Project Cost
                      </div>
                      <div className="text-2xl font-black text-green-700">
                        {formatCurrency(plan.total_project_cost)}
                      </div>
                    </div>
                  </div>

                  {/* Construction Stages Summary */}
                  <div className="mb-6">
                    <h4 className="text-sm font-bold text-gray-700 mb-3 flex items-center">
                      <Zap className="w-4 h-4 mr-1 text-orange-500" />
                      Construction Stages ({plan.construction_stages?.length || 0})
                    </h4>
                    <div className="space-y-2">
                      {(plan.construction_stages || []).slice(0, 3).map((stage, index) => (
                        <div key={index} className="flex items-center justify-between text-sm bg-gray-50 p-2 rounded">
                          <span className="text-gray-700">{stage.stage_name}</span>
                          <span className="font-semibold text-gray-900">
                            {formatCurrency(stage.total_cost)}
                          </span>
                        </div>
                      ))}
                      {(plan.construction_stages || []).length > 3 && (
                        <div className="text-xs text-gray-500 text-center">
                          +{plan.construction_stages.length - 3} more stages...
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Metadata */}
                  <div className="flex items-center text-xs text-gray-500 mb-6 pb-6 border-b border-gray-200">
                    <span className="mr-4">📍 {plan.location}</span>
                    <span>📅 Created {formatDate(plan.created_at)}</span>
                  </div>

                  {/* Actions */}
                  <div className="grid grid-cols-3 gap-2">
                    <Link
                      to={`/house-plans/${plan.id}`}
                      className="flex items-center justify-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium text-sm"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </Link>
                    <button
                      onClick={() => {
                        window.open(`${BACKEND_URL}/api/house-plans/${plan.id}/download-pdf`, '_blank');
                      }}
                      className="flex items-center justify-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium text-sm"
                    >
                      <Download className="w-4 h-4 mr-1" />
                      PDF
                    </button>
                    <button
                      onClick={() => setDeleteModal({ show: true, planId: plan.id })}
                      className="flex items-center justify-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium text-sm"
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {deleteModal.show && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">Delete Plan?</h3>
                  <p className="text-sm text-gray-600">This action cannot be undone</p>
                </div>
              </div>
              <p className="text-gray-700 mb-6">
                Are you sure you want to delete this house plan? All calculations and materials will be permanently removed.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setDeleteModal({ show: false, planId: null })}
                  className="flex-1 px-4 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleDelete(deleteModal.planId)}
                  className="flex-1 px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyHousePlans;
