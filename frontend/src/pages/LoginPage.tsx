import { signInWithPopup } from 'firebase/auth';
import { auth, googleProvider } from '../lib/firebase';
import { Map, Shield, BarChart3, Users } from 'lucide-react';
import { useState } from 'react';

export default function LoginPage() {
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleGoogleLogin = async () => {
    try {
      setError('');
      setLoading(true);
      await signInWithPopup(auth, googleProvider);
    } catch (error: any) {
      console.error('Login failed:', error);
      
      // Provide user-friendly error messages
      if (error.code === 'auth/popup-blocked') {
        setError('Popup was blocked. Please enable popups for this site.');
      } else if (error.code === 'auth/cancelled-popup-request') {
        setError('Sign-in cancelled.');
      } else if (error.code === 'auth/popup-closed-by-user') {
        setError('Sign-in window was closed.');
      } else {
        setError('Failed to sign in. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-200">
            <Map size={32} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Smart Resource Allocation
          </h1>
          <p className="text-gray-500">
            AI-Powered Volunteer Coordination for Social Impact
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 p-8">
          {/* Features */}
          <div className="grid grid-cols-2 gap-3 mb-8">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Shield size={16} className="text-blue-500" />
              <span>AI-Powered</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Map size={16} className="text-green-500" />
              <span>Heat Maps</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <BarChart3 size={16} className="text-purple-500" />
              <span>Smart Allocation</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Users size={16} className="text-orange-500" />
              <span>12 GCP Services</span>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
              {error}
            </div>
          )}

          {/* Google Sign-In Button */}
          <button
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3 bg-white border-2 border-gray-200 rounded-xl px-6 py-3.5 text-gray-700 font-medium hover:bg-gray-50 hover:border-gray-300 hover:shadow-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-gray-400 border-t-gray-700 rounded-full animate-spin" />
                Signing in...
              </>
            ) : (
              <>
                <img
                  src="https://www.google.com/favicon.ico"
                  alt="Google"
                  className="w-5 h-5"
                />
                Sign in with Google
              </>
            )}
          </button>

          <p className="text-xs text-gray-400 mt-6 text-center">
            Google Solution Challenge 2026 | SDG 1, 10, 11, 17
          </p>
        </div>
      </div>
    </div>
  );
}