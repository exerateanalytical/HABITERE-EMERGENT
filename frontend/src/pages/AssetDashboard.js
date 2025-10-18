import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Package, Wrench, TrendingUp, DollarSign, Plus, Calendar, AlertTriangle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const AssetDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentTasks, setRecentTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    fetchDashboardData();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, tasksRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/assets/dashboard/stats`, { withCredentials: true }),
        axios.get(`${BACKEND_URL}/api/assets/maintenance?limit=5`, { withCredentials: true })
      ]);
      
      setStats(statsRes.data);
      setRecentTasks(tasksRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
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
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Asset Management</h1>
            <p className="text-gray-600">Manage property assets and maintenance</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => navigate('/assets/create')}
              className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 flex items-center"
            >
              <Plus className="w-5 h-5 mr-2" />
              Add Asset
            </button>
            <button
              onClick={() => navigate('/assets/maintenance/create')}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 flex items-center"
            >
              <Calendar className="w-5 h-5 mr-2" />
              Create Task
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <Package className="w-10 h-10 text-green-600" />
                <TrendingUp className="w-5 h-5 text-green-500" />
              </div>
              <div className="text-3xl font-bold text-green-600 mb-2">{stats.total_assets}</div>
              <div className="text-gray-600">Total Assets</div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <Wrench className="w-10 h-10 text-blue-600" />
                {stats.active_maintenance_tasks > 0 && (
                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">Active</span>
                )}
              </div>
              <div className="text-3xl font-bold text-blue-600 mb-2">{stats.active_maintenance_tasks}</div>
              <div className="text-gray-600">Active Maintenance</div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <AlertTriangle className="w-10 h-10 text-orange-600" />
                {stats.upcoming_maintenance > 0 && (
                  <span className="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full">Urgent</span>
                )}
              </div>
              <div className="text-3xl font-bold text-orange-600 mb-2">{stats.upcoming_maintenance}</div>
              <div className="text-gray-600">Upcoming Maintenance</div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <DollarSign className="w-10 h-10 text-purple-600" />
              </div>
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {stats.total_expenses ? `${(stats.total_expenses / 1000).toFixed(0)}K` : '0'}
              </div>
              <div className="text-gray-600">Total Expenses (XAF)</div>
            </div>
          </div>
        )}

        {/* Assets by Category */}
        {stats && stats.assets_by_category && stats.assets_by_category.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-bold mb-4">Assets by Category</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {stats.assets_by_category.map((cat, index) => (
                <div key={index} className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{cat.count}</div>
                  <div className="text-sm text-gray-600">{cat.category}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Maintenance Tasks */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Recent Maintenance</h2>
              <button
                onClick={() => navigate('/assets/maintenance')}
                className="text-green-600 hover:text-green-700 font-semibold"
              >
                View All
              </button>
            </div>

            {recentTasks.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Wrench className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p>No maintenance tasks yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentTasks.map((task) => (
                  <div
                    key={task.id}
                    onClick={() => navigate(`/assets/maintenance/${task.id}`)}
                    className="p-4 border rounded-lg hover:border-green-500 cursor-pointer transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold">{task.task_title}</h3>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        task.status === 'Completed' ? 'bg-green-100 text-green-800' :
                        task.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {task.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{task.asset_name}</p>
                    <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                      <span>Priority: {task.priority}</span>
                      <span>{new Date(task.scheduled_date).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <button
                onClick={() => navigate('/assets')}
                className="w-full bg-gray-100 hover:bg-gray-200 p-4 rounded-lg text-left transition-colors flex items-center justify-between"
              >
                <div className="flex items-center">
                  <Package className="w-6 h-6 text-green-600 mr-3" />
                  <div>
                    <div className="font-semibold">View All Assets</div>
                    <div className="text-sm text-gray-600">Browse asset inventory</div>
                  </div>
                </div>
              </button>

              <button
                onClick={() => navigate('/assets/maintenance')}
                className="w-full bg-gray-100 hover:bg-gray-200 p-4 rounded-lg text-left transition-colors flex items-center justify-between"
              >
                <div className="flex items-center">
                  <Wrench className="w-6 h-6 text-blue-600 mr-3" />
                  <div>
                    <div className="font-semibold">Maintenance Tasks</div>
                    <div className="text-sm text-gray-600">Manage maintenance schedule</div>
                  </div>
                </div>
              </button>

              <button
                onClick={() => navigate('/assets/expenses')}
                className="w-full bg-gray-100 hover:bg-gray-200 p-4 rounded-lg text-left transition-colors flex items-center justify-between"
              >
                <div className="flex items-center">
                  <DollarSign className="w-6 h-6 text-purple-600 mr-3" />
                  <div>
                    <div className="font-semibold">View Expenses</div>
                    <div className="text-sm text-gray-600">Track asset expenses</div>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssetDashboard;
