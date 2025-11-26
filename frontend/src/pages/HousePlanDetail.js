import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import {
  Home, ArrowLeft, Download, Trash2, Edit, Building, Layers,
  DollarSign, Clock, MapPin, CheckCircle, Package, Users, Zap,
  FileText, Calculator, TrendingUp, AlertCircle, Calendar
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const HousePlanDetail = () => {
  const { planId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteModal, setDeleteModal] = useState(false);

  useEffect(() => {
    if (user && planId) {
      fetchPlanDetails();
    }
  }, [user, planId]);

  const fetchPlanDetails = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${BACKEND_URL}/api/house-plans/${planId}`,
        { withCredentials: true }
      );
      setPlan(response.data.plan);
    } catch (error) {
      console.error('Error fetching plan:', error);
      setError(error.response?.data?.detail || 'Failed to load plan details');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await axios.delete(
        `${BACKEND_URL}/api/house-plans/${planId}`,
        { withCredentials: true }
      );
      alert('Plan deleted successfully');
      navigate('/house-plans/my-plans');
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
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading plan details...</p>
        </div>
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Plan Not Found</h2>
          <p className="text-gray-600 mb-6">{error || 'The requested plan could not be found'}</p>
          <Link
            to="/house-plans/my-plans"
            className="inline-flex items-center bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to My Plans
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <Link
            to="/house-plans/my-plans"
            className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to My Plans
          </Link>
          
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h1 className="text-3xl font-black text-gray-900 mb-2">{plan.name}</h1>
                {plan.description && (
                  <p className="text-gray-600 mb-4">{plan.description}</p>
                )}
                <div className="flex flex-wrap gap-3">
                  <span className="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                    <Building className="w-4 h-4 mr-1" />
                    {plan.house_type.replace('_', ' ').toUpperCase()}
                  </span>
                  <span className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    <MapPin className="w-4 h-4 mr-1" />
                    {plan.location}
                  </span>
                  <span className="inline-flex items-center px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                    <Clock className="w-4 h-4 mr-1" />
                    Created {formatDate(plan.created_at)}
                  </span>
                </div>
              </div>
              
              <div className="flex gap-2 ml-4">
                <button
                  onClick={() => window.open(`${BACKEND_URL}/api/house-plans/${plan.id}/download-pdf`, '_blank')}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
                >
                  <Download className="w-5 h-5 mr-2" />
                  Download PDF
                </button>
                <button
                  onClick={() => setDeleteModal(true)}
                  className="inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Cost Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between mb-2">
              <Package className="w-8 h-8 text-green-600" />
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <div className="text-sm text-gray-600">Materials Cost</div>
            <div className="text-2xl font-black text-gray-900">
              {formatCurrency(plan.total_materials_cost)}
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between mb-2">
              <Users className="w-8 h-8 text-blue-600" />
              <TrendingUp className="w-5 h-5 text-blue-500" />
            </div>
            <div className="text-sm text-gray-600">Labor Cost</div>
            <div className="text-2xl font-black text-gray-900">
              {formatCurrency(plan.labor_cost)}
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
            <div className="flex items-center justify-between mb-2">
              <DollarSign className="w-8 h-8 text-purple-600" />
              <CheckCircle className="w-5 h-5 text-purple-500" />
            </div>
            <div className="text-sm text-gray-600">Total Project Cost</div>
            <div className="text-2xl font-black text-purple-900">
              {formatCurrency(plan.total_project_cost)}
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-orange-500">
            <div className="flex items-center justify-between mb-2">
              <Clock className="w-8 h-8 text-orange-600" />
              <Calendar className="w-5 h-5 text-orange-500" />
            </div>
            <div className="text-sm text-gray-600">Estimated Duration</div>
            <div className="text-2xl font-black text-gray-900">
              {plan.estimated_duration_days} days
            </div>
          </div>
        </div>

        {/* Project Specifications */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <FileText className="w-6 h-6 mr-2 text-green-600" />
            Project Specifications
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Total Floor Area</div>
              <div className="text-lg font-bold text-gray-900">{plan.total_floor_area.toFixed(2)} m²</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Total Built Area</div>
              <div className="text-lg font-bold text-gray-900">{plan.total_built_area.toFixed(2)} m²</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Number of Floors</div>
              <div className="text-lg font-bold text-gray-900">{plan.floors.length}</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Total Rooms</div>
              <div className="text-lg font-bold text-gray-900">
                {plan.floors.reduce((sum, floor) => sum + floor.rooms.length, 0)}
              </div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Foundation Type</div>
              <div className="text-lg font-bold text-gray-900 capitalize">{plan.foundation_type}</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Wall Type</div>
              <div className="text-lg font-bold text-gray-900 capitalize">{plan.wall_type}</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Roofing Type</div>
              <div className="text-lg font-bold text-gray-900 capitalize">{plan.roofing_type}</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Finishing Level</div>
              <div className="text-lg font-bold text-gray-900 capitalize">{plan.finishing_level}</div>
            </div>
          </div>
        </div>

        {/* Floor Plans */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Layers className="w-6 h-6 mr-2 text-green-600" />
            Floor Plans
          </h2>
          
          {plan.floors.map((floor, floorIndex) => (
            <div key={floorIndex} className="mb-8 last:mb-0">
              <h3 className="text-lg font-bold text-gray-900 mb-4 pb-2 border-b-2 border-green-500">
                {floor.floor_name}
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {floor.rooms.map((room, roomIndex) => (
                  <div key={roomIndex} className="bg-gradient-to-br from-green-50 to-blue-50 p-4 rounded-lg border-2 border-green-200">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-bold text-gray-900">{room.name}</h4>
                        <p className="text-sm text-gray-600 capitalize">{room.type.replace('_', ' ')}</p>
                      </div>
                      <Building className="w-8 h-8 text-green-600" />
                    </div>
                    <div className="space-y-1 mt-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Dimensions:</span>
                        <span className="font-semibold">{room.length}m × {room.width}m</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Height:</span>
                        <span className="font-semibold">{room.height}m</span>
                      </div>
                      <div className="flex justify-between text-sm pt-2 border-t border-green-300">
                        <span className="text-gray-700 font-medium">Area:</span>
                        <span className="font-bold text-green-700">{(room.length * room.width).toFixed(2)} m²</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-4 bg-green-100 p-3 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-gray-900">Total Floor Area:</span>
                  <span className="text-xl font-black text-green-700">
                    {floor.rooms.reduce((sum, room) => sum + (room.length * room.width), 0).toFixed(2)} m²
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Construction Stages & BOQ */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Calculator className="w-6 h-6 mr-2 text-green-600" />
            Bill of Quantities (BOQ) - Construction Stages
          </h2>
          
          <div className="space-y-6">
            {plan.construction_stages.map((stage, index) => (
              <div key={index} className="border-2 border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gradient-to-r from-green-500 to-blue-500 p-4 text-white">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center font-black text-lg mr-3">
                        {stage.stage_order}
                      </div>
                      <div>
                        <h3 className="text-lg font-bold">{stage.stage_name}</h3>
                        <p className="text-sm text-green-100">Duration: {stage.duration_days} days</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-black">{formatCurrency(stage.total_cost)}</div>
                      <div className="text-xs text-green-100">{stage.materials.length} items</div>
                    </div>
                  </div>
                </div>
                
                <div className="p-4">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-100">
                        <tr>
                          <th className="px-4 py-2 text-left font-semibold text-gray-700">Item</th>
                          <th className="px-4 py-2 text-left font-semibold text-gray-700">Unit</th>
                          <th className="px-4 py-2 text-right font-semibold text-gray-700">Quantity</th>
                          <th className="px-4 py-2 text-right font-semibold text-gray-700">Unit Price</th>
                          <th className="px-4 py-2 text-right font-semibold text-gray-700">Total</th>
                        </tr>
                      </thead>
                      <tbody>
                        {stage.materials.map((material, mIndex) => (
                          <tr key={mIndex} className={mIndex % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                            <td className="px-4 py-2">
                              <div className="font-medium text-gray-900">{material.item_name}</div>
                              {material.specification && (
                                <div className="text-xs text-gray-500">{material.specification}</div>
                              )}
                            </td>
                            <td className="px-4 py-2 text-gray-700">{material.unit}</td>
                            <td className="px-4 py-2 text-right font-medium">{material.quantity.toFixed(2)}</td>
                            <td className="px-4 py-2 text-right">{formatCurrency(material.unit_price)}</td>
                            <td className="px-4 py-2 text-right font-bold text-green-700">
                              {formatCurrency(material.total_price)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-8 flex gap-4">
          <button
            onClick={() => window.open(`${BACKEND_URL}/api/house-plans/${plan.id}/download-pdf`, '_blank')}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white px-6 py-4 rounded-lg font-bold flex items-center justify-center"
          >
            <Download className="w-5 h-5 mr-2" />
            Download Complete Plan as PDF
          </button>
          <Link
            to="/house-plans/builder"
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-4 rounded-lg font-bold flex items-center justify-center"
          >
            <Home className="w-5 h-5 mr-2" />
            Create New Plan
          </Link>
        </div>

        {/* Delete Confirmation Modal */}
        {deleteModal && (
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
                Are you sure you want to delete "{plan.name}"? All floor plans, calculations, and materials will be permanently removed.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setDeleteModal(false)}
                  className="flex-1 px-4 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
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

export default HousePlanDetail;
