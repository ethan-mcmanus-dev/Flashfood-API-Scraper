/**
 * Navigation bar component.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center">
              <span className="text-2xl font-bold text-primary-600">
                🍽️ Flashfood Tracker
              </span>
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            <Link
              to="/preferences"
              className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
            >
              My Preferences
            </Link>

            <span className="text-sm text-gray-700">
              {user?.full_name || user?.email}
            </span>

            <button
              onClick={logout}
              className="px-4 py-2 text-sm font-medium text-white bg-gray-600 hover:bg-gray-700 rounded-md transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};
