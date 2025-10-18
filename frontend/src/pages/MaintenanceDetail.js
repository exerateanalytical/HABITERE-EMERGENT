import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Wrench, ArrowLeft, Clock, DollarSign, User, Calendar, CheckCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const MaintenanceDetail = () => {
  const navigate = useNavigate();
  const { taskId } = useParams();
  const { user } = useAuth();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [actualCost, setActualCost] = useState('');

  useEffect(() => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    fetchTask();
  }, [user, taskId]);

  const fetchTask = async () => {
    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/assets/maintenance/${taskId}`,
        { withCredentials: true }
      );
      setTask(response.data);
    } catch (error) {
      console.error('Error fetching task:', error);
      alert('Failed to load task');
    } finally {
      setLoading(false);
    }
  };

  const updateTaskStatus = async (newStatus) => {
    if (newStatus === 'Completed' && !actualCost) {
      const cost = prompt('Enter actual cost (XAF):');
      if (!cost) return;
      setActualCost(cost);
    }

    setUpdating(true);
    try {
      const payload = {
        status: newStatus
      };
      if (newStatus === 'Completed' && actualCost) {
        payload.actual_cost = parseFloat(actualCost);
      }

      await axios.put(
        `${BACKEND_URL}/api/assets/maintenance/${taskId}/status`,
        payload,
        { withCredentials: true }
      );
      alert('Task status updated successfully!');
      fetchTask();
    } catch (error) {
      console.error('Error updating task:', error);
      alert(error.response?.data?.detail || 'Failed to update task');
    } finally {
      setUpdating(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Completed':
        return 'bg-green-100 text-green-800';
      case 'In Progress':
        return 'bg-blue-100 text-blue-800';
      case 'Pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'High':
        return 'bg-red-100 text-red-800';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'Low':
        return 'bg-green-100 text-green-800';
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

  if (!task) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-700 mb-2">Task not found</h2>
          <button
            onClick={() => navigate('/assets/maintenance')}
            className="text-green-600 hover:text-green-700 font-semibold"
          >
            Back to Maintenance
          </button>
        </div>
      </div>
    );
  }

  const canUpdateStatus = 
    task.assigned_to === user?.id || 
    ['estate_manager', 'admin'].includes(user?.role);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/assets/maintenance')}
            className="text-green-600 hover:text-green-700 font-semibold mb-4 flex items-center"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Maintenance
          </button>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-2">{task.task_title}</h1>
              <p className="text-gray-600">Task Details</p>
            </div>
            <Wrench className="w-12 h-12 text-blue-600" />
          </div>
        </div>

        {/* Status and Priority */}
        <div className="flex gap-3 mb-8">
          <span className={`px-4 py-2 rounded-full font-semibold ${getStatusColor(task.status)}`}>
            {task.status}
          </span>
          <span className={`px-4 py-2 rounded-full font-semibold ${getPriorityColor(task.priority)}`}>
            {task.priority} Priority
          </span>
        </div>

        {/* Main Info Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Task Information</h2>
          
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-600">Description</label>
              <p className="text-gray-900 mt-1">{task.description}</p>
            </div>

            {task.asset_name && (
              <div>
                <label className="text-sm font-medium text-gray-600">Asset</label>
                <p className="text-gray-900 mt-1">{task.asset_name}</p>
              </div>
            )}

            {task.notes && (
              <div>
                <label className="text-sm font-medium text-gray-600">Notes</label>
                <p className="text-gray-900 mt-1">{task.notes}</p>
              </div>
            )}
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-4">
              <Calendar className="w-6 h-6 text-blue-600 mr-3" />
              <h3 className="font-bold">Schedule</h3>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-sm text-gray-600">Scheduled Date</label>
                <p className="font-medium">{new Date(task.scheduled_date).toLocaleDateString()}</p>
              </div>
              {task.completion_date && (
                <div>
                  <label className="text-sm text-gray-600">Completion Date</label>
                  <p className="font-medium">{new Date(task.completion_date).toLocaleDateString()}</p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-4">
              <DollarSign className="w-6 h-6 text-green-600 mr-3" />
              <h3 className="font-bold">Cost</h3>
            </div>
            <div className="space-y-3">
              {task.estimated_cost && (
                <div>
                  <label className="text-sm text-gray-600">Estimated Cost</label>
                  <p className="font-medium">{task.estimated_cost.toLocaleString()} XAF</p>
                </div>
              )}
              {task.actual_cost && (
                <div>
                  <label className="text-sm text-gray-600">Actual Cost</label>
                  <p className="font-medium">{task.actual_cost.toLocaleString()} XAF</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Attachments */}
        {task.attachments && task.attachments.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="font-bold mb-4">Attachments</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {task.attachments.map((attachment, index) => (
                <div key={index} className="bg-gray-100 p-4 rounded-lg">
                  <div className="text-sm text-gray-600">File {index + 1}</div>
                  <a
                    href={attachment}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-green-600 hover:text-green-700 text-sm"
                  >
                    View
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        {canUpdateStatus && task.status !== 'Completed' && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="font-bold mb-4">Update Status</h3>
            <div className="flex gap-3">
              {task.status === 'Pending' && (
                <button
                  onClick={() => updateTaskStatus('In Progress')}
                  disabled={updating}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {updating ? 'Updating...' : 'Start Task'}
                </button>
              )}
              {task.status === 'In Progress' && (
                <button
                  onClick={() => updateTaskStatus('Completed')}
                  disabled={updating}
                  className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400 flex items-center"
                >
                  <CheckCircle className="w-5 h-5 mr-2" />
                  {updating ? 'Updating...' : 'Mark as Completed'}
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MaintenanceDetail;
