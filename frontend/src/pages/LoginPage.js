import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import SEOHead from '../components/SEOHead';
import { generateSEOData } from '../utils/seoData';
import { 
  Eye, 
  EyeOff, 
  Mail, 
  Lock, 
  Building,
  ArrowLeft,
  Smartphone,
  Shield,
  CheckCircle,
  Star,
  Users,
  Home
} from 'lucide-react';

const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  // Generate SEO data for login page
  const seoData = generateSEOData('login', {
    location: 'Cameroon'
  });

  const handleEmergentLogin = () => {
    const redirectUrl = `${window.location.origin}/auth/callback`;
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // This would integrate with your backend auth endpoint
      const response = await login(email, password);
      if (response.success) {
        navigate('/dashboard');
      } else {
        setError(response.message || 'Login failed');
      }
    } catch (err) {
      setError('Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Get the Google OAuth URL from backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/google/login`, {
        credentials: 'include'
      });
      const data = await response.json();
      
      // Redirect to Google OAuth
      window.location.href = data.auth_url;
    } catch (err) {
      console.error('Google login error:', err);
      setError('Failed to initiate Google login. Please try again.');
      setLoading(false);
    }
  };

  const handleFacebookLogin = () => {
    // This would integrate with Facebook OAuth
    setError('Facebook login coming soon!');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <SEOHead
        title="Login to Habitere - Access Your Property Dashboard | Cameroon Real Estate"
        description="Login to Habitere to access your property dashboard, manage listings, connect with clients, and grow your real estate business in Cameroon."
        keywords="login habitere, property dashboard cameroon, real estate login, yaoundé property management, douala real estate access"
        focusKeyword="login habitere cameroon"
        ogImage="https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1200&q=80"
        location="Cameroon"
      />

      <div className="max-w-6xl w-full space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          {/* Left Side - Login Form */}
          <div className="bg-white rounded-3xl shadow-2xl border border-gray-100 p-8 lg:p-12">
            {/* Back to home link */}
            <div className="mb-6">
              <Link 
                to="/" 
                className="inline-flex items-center text-sm text-gray-600 hover:text-blue-600 transition-colors duration-200"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
              </Link>
            </div>

            {/* Header */}
            <div className="text-center mb-8">
              <div className="flex items-center justify-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <Building className="w-8 h-8 text-white" />
                </div>
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
              <p className="text-gray-600">Sign in to access your Habitere dashboard</p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-2xl">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            {/* Quick Login Options */}
            <div className="space-y-4 mb-8">
              {/* Emergent Auth Login */}
              <button
                onClick={handleEmergentLogin}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center group"
              >
                <Shield className="w-5 h-5 mr-3 group-hover:scale-110 transition-transform duration-300" />
                Continue with Emergent Auth
              </button>

              {/* Social Login Options */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <button
                  onClick={handleGoogleLogin}
                  className="flex items-center justify-center px-4 py-3 border border-gray-200 rounded-2xl shadow-lg hover:shadow-xl bg-white hover:bg-gray-50 transition-all duration-300 group"
                >
                  <div className="w-5 h-5 mr-3 bg-red-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs font-bold">G</span>
                  </div>
                  <span className="text-gray-700 font-medium group-hover:text-gray-900">Google</span>
                </button>
                
                <button
                  onClick={handleFacebookLogin}
                  className="flex items-center justify-center px-4 py-3 border border-gray-200 rounded-2xl shadow-lg hover:shadow-xl bg-white hover:bg-gray-50 transition-all duration-300 group"
                >
                  <div className="w-5 h-5 mr-3 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs font-bold">f</span>
                  </div>
                  <span className="text-gray-700 font-medium group-hover:text-gray-900">Facebook</span>
                </button>
              </div>
            </div>

            {/* Divider */}
            <div className="relative mb-8">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500 font-medium">Or continue with email</span>
              </div>
            </div>

            {/* Email Login Form */}
            <form onSubmit={handleEmailLogin} className="space-y-6">
              {/* Email Field */}
              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-12 pr-4 py-4 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 text-gray-900 placeholder-gray-500"
                    placeholder="Enter your email"
                  />
                </div>
              </div>

              {/* Password Field */}
              <div>
                <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-12 pr-12 py-4 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 text-gray-900 placeholder-gray-500"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Remember Me & Forgot Password */}
              <div className="flex items-center justify-between">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Remember me</span>
                </label>
                <Link
                  to="/forgot-password"
                  className="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors duration-200"
                >
                  Forgot password?
                </Link>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-bold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center"
              >
                {loading ? (
                  <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  'Sign In'
                )}
              </button>
            </form>

            {/* Sign Up Link */}
            <div className="mt-8 text-center">
              <p className="text-gray-600">
                Don't have an account?{' '}
                <Link
                  to="/register"
                  className="font-semibold text-blue-600 hover:text-blue-700 transition-colors duration-200"
                >
                  Sign up for free
                </Link>
              </p>
            </div>
          </div>

          {/* Right Side - Marketing Content */}
          <div className="hidden lg:block space-y-8">
            {/* Hero Content */}
            <div className="text-center">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Join Cameroon's Leading
                <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Real Estate Platform</span>
              </h2>
              <p className="text-xl text-gray-600 leading-relaxed">
                Access thousands of verified properties, connect with trusted professionals, 
                and manage your real estate business with ease.
              </p>
            </div>

            {/* Features Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
                <div className="w-12 h-12 bg-blue-100 rounded-2xl flex items-center justify-center mb-4">
                  <Home className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">1000+ Properties</h3>
                <p className="text-gray-600 text-sm">Verified listings across all regions of Cameroon</p>
              </div>

              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
                <div className="w-12 h-12 bg-purple-100 rounded-2xl flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">500+ Professionals</h3>
                <p className="text-gray-600 text-sm">Certified experts ready to help you</p>
              </div>

              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
                <div className="w-12 h-12 bg-green-100 rounded-2xl flex items-center justify-center mb-4">
                  <Smartphone className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">MTN MoMo Payments</h3>
                <p className="text-gray-600 text-sm">Secure payments with Mobile Money</p>
              </div>

              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
                <div className="w-12 h-12 bg-orange-100 rounded-2xl flex items-center justify-center mb-4">
                  <Star className="w-6 h-6 text-orange-600" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">4.9★ Rated</h3>
                <p className="text-gray-600 text-sm">Trusted by thousands of users</p>
              </div>
            </div>

            {/* Testimonial */}
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-3xl p-8 border border-white/20">
              <div className="flex items-center space-x-4 mb-6">
                <img
                  src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&q=80"
                  alt="User testimonial"
                  className="w-16 h-16 rounded-full object-cover"
                />
                <div>
                  <h4 className="text-lg font-bold text-gray-900">Jean-Paul Mbida</h4>
                  <p className="text-gray-600">Property Developer, Yaoundé</p>
                  <div className="flex items-center space-x-1 mt-1">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                    ))}
                  </div>
                </div>
              </div>
              <p className="text-gray-700 italic leading-relaxed">
                "Habitere has transformed how I manage my properties. The platform is intuitive, 
                secure, and the MTN MoMo integration makes payments seamless for my tenants."
              </p>
            </div>

            {/* Trust Indicators */}
            <div className="flex items-center justify-center space-x-8 pt-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-6 h-6 text-green-500" />
                <span className="text-sm font-medium text-gray-700">Verified Platform</span>
              </div>
              <div className="flex items-center space-x-2">
                <Shield className="w-6 h-6 text-blue-500" />
                <span className="text-sm font-medium text-gray-700">Secure & Encrypted</span>
              </div>
              <div className="flex items-center space-x-2">
                <Users className="w-6 h-6 text-purple-500" />
                <span className="text-sm font-medium text-gray-700">10K+ Users</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;