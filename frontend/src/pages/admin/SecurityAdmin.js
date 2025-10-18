import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import { Shield, CheckCircle, XCircle, Eye, TrendingUp, Users, Briefcase, Calendar } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const SecurityAdmin = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('applications'); // applications, services, analytics
  const [applications, setApplications] = useState([]);
  const [services, setServices] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/auth/login');
      return;
    }
    if (user.role !== 'security_admin' && user.role !== 'admin') {
      alert('Access denied. Security admins only.');
      navigate('/security');
      return;
    }
    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      const [appsRes, servicesRes, statsRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/security/guards/applications`, { withCredentials: true }),
        axios.get(`${BACKEND_URL}/api/security/services`, { withCredentials: true }),
        axios.get(`${BACKEND_URL}/api/security/stats`)
      ]);
      
      setApplications(appsRes.data);
      setServices(servicesRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveApplication = async (applicationId) => {
    if (!window.confirm('Approve this guard application?')) return;
    
    try {
      await axios.put(
        `${BACKEND_URL}/api/security/guards/applications/${applicationId}/approve`,
        {},
        { withCredentials: true }
      );
      alert('Application approved successfully!');
      fetchData();
    } catch (error) {
      console.error('Error approving application:', error);
      alert(error.response?.data?.detail || 'Failed to approve application');
    }
  };

  const handleRejectApplication = async (applicationId) => {
    if (!window.confirm('Reject this guard application?')) return;
    
    // Note: We'd need to add a reject endpoint to backend
    alert('Reject functionality to be implemented');
  };

  const handleDeleteService = async (serviceId) => {
    if (!window.confirm('Delete this service? This action cannot be undone.')) return;
    
    try {
      await axios.delete(
        `${BACKEND_URL}/api/security/services/${serviceId}`,
        { withCredentials: true }
      );
      alert('Service deleted successfully');
      fetchData();
    } catch (error) {
      console.error('Error deleting service:', error);
      alert('Failed to delete service');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  const pendingApplications = applications.filter(a => a.status === 'pending');
  const approvedApplications = applications.filter(a => a.status === 'approved');

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Security Administration</h1>
          <p className="text-gray-600">Manage guard applications, services, and platform analytics</p>
        </div>

        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-3">
                <Briefcase className="w-8 h-8 text-green-600" />
                <TrendingUp className="w-5 h-5 text-green-500" />
              </div>
              <div className="text-3xl font-bold text-green-600 mb-2">{stats.total_services}</div>
              <div className="text-gray-600">Total Services</div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-3">
                <Shield className="w-8 h-8 text-blue-600" />
                <TrendingUp className="w-5 h-5 text-blue-500" />
              </div>
              <div className="text-3xl font-bold text-blue-600 mb-2">{stats.available_guards}</div>
              <div className="text-gray-600">Verified Guards</div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-3">
                <Calendar className="w-8 h-8 text-purple-600" />
                <TrendingUp className="w-5 h-5 text-purple-500" />
              </div>
              <div className="text-3xl font-bold text-purple-600 mb-2">{stats.total_bookings}</div>
              <div className="text-gray-600">Total Bookings</div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-3">
                <Users className="w-8 h-8 text-orange-600" />
                <span className={`text-xs px-2 py-1 rounded-full ${
                  stats.pending_applications > 0 ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-600'
                }`}>
                  {stats.pending_applications > 0 ? 'Action Required' : 'None'}
                </span>
              </div>
              <div className="text-3xl font-bold text-orange-600 mb-2">{stats.pending_applications}</div>
              <div className="text-gray-600">Pending Applications</div>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('applications')}
              className={`px-6 py-4 font-semibold ${
                activeTab === 'applications'
                  ? 'text-green-600 border-b-2 border-green-600'
                  : 'text-gray-600 hover:text-green-600'
              }`}
            >
              Guard Applications ({pendingApplications.length} pending)
            </button>
            <button
              onClick={() => setActiveTab('services')}
              className={`px-6 py-4 font-semibold ${
                activeTab === 'services'
                  ? 'text-green-600 border-b-2 border-green-600'
                  : 'text-gray-600 hover:text-green-600'
              }`}
            >
              Security Services ({services.length})
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-6 py-4 font-semibold ${
                activeTab === 'analytics'
                  ? 'text-green-600 border-b-2 border-green-600'
                  : 'text-gray-600 hover:text-green-600'
              }`}
            >
              Analytics
            </button>
          </div>
        </div>

        {/* Applications Tab */}
        {activeTab === 'applications' && (
          <div>
            <div className="mb-6">
              <h2 className="text-xl font-bold mb-4">Pending Applications ({pendingApplications.length})</h2>
              {pendingApplications.length === 0 ? (
                <div className="bg-white rounded-lg shadow-md p-8 text-center">
                  <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-3" />
                  <p className="text-gray-600">No pending applications</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {pendingApplications.map((app) => (
                    <div key={app.id} className="bg-white rounded-lg shadow-md p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-xl font-bold mb-1">{app.full_name}</h3>
                          <p className="text-gray-600">{app.email} • {app.phone}</p>
                        </div>
                        <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-semibold">
                          Pending Review
                        </span>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div>
                          <div className="text-sm text-gray-600">Experience</div>
                          <div className="font-semibold">{app.experience_years} years</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-600">City</div>
                          <div className="font-semibold">{app.city}</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-600">Availability</div>
                          <div className="font-semibold">{app.availability}</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-600">Applied</div>
                          <div className="font-semibold text-sm">{new Date(app.applied_at).toLocaleDateString()}</div>
                        </div>
                      </div>

                      {app.certifications && app.certifications.length > 0 && (
                        <div className="mb-4">
                          <div className="text-sm text-gray-600 mb-2">Certifications</div>
                          <div className="flex flex-wrap gap-2">
                            {app.certifications.map((cert, idx) => (
                              <span key={idx} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                                {cert}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {app.previous_employers && app.previous_employers.length > 0 && (
                        <div className="mb-4">
                          <div className="text-sm text-gray-600 mb-2">Previous Employers</div>
                          <div className="text-sm">{app.previous_employers.join(', ')}</div>
                        </div>
                      )}

                      <div className="flex gap-3">
                        <button
                          onClick={() => handleApproveApplication(app.id)}
                          className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 font-semibold flex items-center"
                        >
                          <CheckCircle className="w-5 h-5 mr-2" />
                          Approve
                        </button>
                        <button
                          onClick={() => handleRejectApplication(app.id)}
                          className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 font-semibold flex items-center"
                        >
                          <XCircle className="w-5 h-5 mr-2" />
                          Reject
                        </button>
                        <button
                          onClick={() => navigate(`/security/guards/${app.id}`)}
                          className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300 font-semibold flex items-center"
                        >
                          <Eye className="w-5 h-5 mr-2" />
                          View Full Profile
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="mb-6">
              <h2 className="text-xl font-bold mb-4">Approved Guards ({approvedApplications.length})</h2>
              {approvedApplications.length === 0 ? (
                <div className="bg-white rounded-lg shadow-md p-8 text-center">
                  <Shield className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-600">No approved guards yet</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {approvedApplications.map((guard) => (
                    <div key={guard.id} className="bg-white rounded-lg shadow-md p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-bold">{guard.full_name}</h3>
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{guard.city}</p>
                      <div className="flex items-center justify-between text-sm">
                        <span>{guard.experience_years} years exp.</span>
                        <button
                          onClick={() => navigate(`/security/guards/${guard.id}`)}
                          className="text-green-600 hover:text-green-700 font-semibold"
                        >
                          View Profile
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Services Tab */}
        {activeTab === 'services' && (
          <div>
            <div className="mb-4">
              <h2 className="text-xl font-bold">All Security Services ({services.length})</h2>
            </div>
            {services.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <Briefcase className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No services available</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {services.map((service) => (
                  <div key={service.id} className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-bold text-lg mb-1">{service.title}</h3>
                        <p className="text-sm text-gray-600">{service.service_type}</p>
                      </div>
                      {service.verified && (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      )}
                    </div>

                    <p className="text-sm text-gray-700 mb-3 line-clamp-2">{service.description}</p>

                    <div className="flex items-center justify-between text-sm mb-4">
                      <div>
                        <div className="text-gray-600">Provider</div>
                        <div className="font-semibold">{service.provider_name}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Bookings</div>
                        <div className="font-semibold">{service.booking_count || 0}</div>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => navigate(`/security/services/${service.id}`)}
                        className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 text-sm"
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleDeleteService(service.id)}
                        className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && stats && (
          <div>
            <h2 className="text-xl font-bold mb-6">Platform Analytics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold mb-4">Service Breakdown</h3>
                <div className="space-y-3">
                  {['Security Guards', 'CCTV Installation', 'Remote Monitoring', 'Patrol Units', 'K9 Units', 'Emergency Response'].map((type) => {
                    const count = services.filter(s => s.service_type === type).length;
                    const percentage = services.length > 0 ? (count / services.length * 100).toFixed(1) : 0;
                    return (
                      <div key={type}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-gray-600">{type}</span>
                          <span className="text-sm font-semibold">{count} ({percentage}%)</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-green-600 h-2 rounded-full" style={{ width: `${percentage}%` }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold mb-4">Application Status</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg">
                    <div>
                      <div className="font-semibold">Pending</div>
                      <div className="text-sm text-gray-600">Awaiting review</div>
                    </div>
                    <div className="text-2xl font-bold text-yellow-600">{pendingApplications.length}</div>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                    <div>
                      <div className="font-semibold">Approved</div>
                      <div className="text-sm text-gray-600">Active guards</div>
                    </div>
                    <div className="text-2xl font-bold text-green-600">{approvedApplications.length}</div>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <div className="font-semibold">Total Applications</div>
                      <div className="text-sm text-gray-600">All time</div>
                    </div>
                    <div className="text-2xl font-bold text-gray-600">{applications.length}</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold mb-4">Platform Overview</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600 mb-2">{stats.total_services}</div>
                  <div className="text-sm text-gray-600">Active Services</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600 mb-2">{stats.available_guards}</div>
                  <div className="text-sm text-gray-600">Verified Guards</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600 mb-2">{stats.total_bookings}</div>
                  <div className="text-sm text-gray-600">Total Bookings</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-orange-600 mb-2">
                    {services.length > 0 ? (services.reduce((sum, s) => sum + (s.booking_count || 0), 0) / services.length).toFixed(1) : 0}
                  </div>
                  <div className="text-sm text-gray-600">Avg Bookings/Service</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SecurityAdmin;
