import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { 
  Users, Building, Wrench, Calendar, DollarSign, 
  TrendingUp, AlertCircle, CheckCircle, Clock, XCircle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/admin/stats`, {
        withCredentials: true
      });
      setStats(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError(err.response?.data?.detail || 'Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Link to="/dashboard" className="btn-primary">
            Go to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Users',
      value: stats?.users?.total || 0,
      change: `+${stats?.users?.new_this_week || 0} this week`,
      icon: Users,
      color: 'bg-blue-500',
      link: '/admin/users'
    },
    {
      title: 'Properties',
      value: stats?.properties?.total || 0,
      change: `${stats?.properties?.pending || 0} pending`,
      icon: Building,
      color: 'bg-green-500',
      link: '/admin/properties'
    },
    {
      title: 'Services',
      value: stats?.services?.total || 0,
      change: `${stats?.services?.pending || 0} pending`,
      icon: Wrench,
      color: 'bg-purple-500',
      link: '/admin/services'
    },
    {
      title: 'Bookings',
      value: stats?.bookings?.total || 0,
      change: `${stats?.bookings?.pending || 0} pending`,
      icon: Calendar,
      color: 'bg-orange-500',
      link: '/admin/bookings'
    },
    {
      title: 'Revenue',
      value: `${(stats?.revenue?.total || 0).toLocaleString()} XAF`,
      change: 'Total earnings',
      icon: DollarSign,
      color: 'bg-yellow-500',
      link: '/admin/analytics'
    }
  ];

  const pendingActions = [
    {
      title: 'Pending Users',
      count: stats?.users?.pending || 0,
      link: '/admin/users?status=pending',
      icon: Clock,
      color: 'text-yellow-600'
    },
    {
      title: 'Pending Properties',
      count: stats?.properties?.pending || 0,
      link: '/admin/properties?status=pending',
      icon: Clock,
      color: 'text-orange-600'
    },
    {
      title: 'Pending Services',
      count: stats?.services?.pending || 0,
      link: '/admin/services?status=pending',
      icon: Clock,
      color: 'text-purple-600'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="mt-1 text-sm text-gray-500">Manage and monitor your platform</p>
            </div>
            <button
              onClick={fetchStats}
              className="btn-primary flex items-center"
            >
              <TrendingUp className="w-5 h-5 mr-2" />
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 mb-8">
          {statCards.map((card, index) => {
            const Icon = card.icon;
            return (
              <Link
                key={index}
                to={card.link}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`${card.color} p-3 rounded-lg`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                </div>
                <h3 className="text-gray-500 text-sm font-medium mb-1">{card.title}</h3>
                <p className="text-2xl font-bold text-gray-900 mb-1">{card.value}</p>
                <p className="text-xs text-gray-500">{card.change}</p>
              </Link>
            );
          })}
        </div>

        {/* Pending Actions */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Pending Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {pendingActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <Link
                  key={index}
                  to={action.link}
                  className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-500 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 mb-1">{action.title}</p>
                      <p className="text-3xl font-bold text-gray-900">{action.count}</p>
                    </div>
                    <Icon className={`w-10 h-10 ${action.color}`} />
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Link
            to="/admin/users"
            className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 hover:bg-blue-100 transition-colors"
          >
            <Users className="w-8 h-8 text-blue-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-1">Manage Users</h3>
            <p className="text-sm text-gray-600">View and verify user accounts</p>
          </Link>

          <Link
            to="/admin/properties"
            className="bg-green-50 border-2 border-green-200 rounded-lg p-6 hover:bg-green-100 transition-colors"
          >
            <Building className="w-8 h-8 text-green-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-1">Moderate Properties</h3>
            <p className="text-sm text-gray-600">Review property listings</p>
          </Link>

          <Link
            to="/admin/services"
            className="bg-purple-50 border-2 border-purple-200 rounded-lg p-6 hover:bg-purple-100 transition-colors"
          >
            <Wrench className="w-8 h-8 text-purple-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-1">Verify Services</h3>
            <p className="text-sm text-gray-600">Approve service providers</p>
          </Link>

          <Link
            to="/admin/analytics"
            className="bg-orange-50 border-2 border-orange-200 rounded-lg p-6 hover:bg-orange-100 transition-colors"
          >
            <TrendingUp className="w-8 h-8 text-orange-600 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-1">Analytics</h3>
            <p className="text-sm text-gray-600">View platform insights</p>
          </Link>
        </div>

        {/* Stats Summary */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Summary</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-gray-900">{stats?.users?.approved || 0}</p>
              <p className="text-sm text-gray-600">Approved Users</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <CheckCircle className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-gray-900">{stats?.properties?.verified || 0}</p>
              <p className="text-sm text-gray-600">Verified Properties</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <CheckCircle className="w-8 h-8 text-purple-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-gray-900">{stats?.services?.verified || 0}</p>
              <p className="text-sm text-gray-600">Verified Services</p>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <Calendar className="w-8 h-8 text-orange-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-gray-900">{stats?.bookings?.total || 0}</p>
              <p className="text-sm text-gray-600">Total Bookings</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
